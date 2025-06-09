"""
LLM-based Query Validator using LLaMA 3 8B via Groq API.
Implements Bonus #2 (Safe & Aligned Behavior) and #3 (Lightweight Model).
"""
import os
import json
from typing import Dict, Any, Tuple, Optional
from enum import Enum
from groq import Groq
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Risultati possibili della validazione."""
    APPROVED = "approved"
    REJECTED_INAPPROPRIATE = "rejected_inappropriate" 
    REJECTED_UNSAFE = "rejected_unsafe"
    REJECTED_OFF_TOPIC = "rejected_off_topic"
    ERROR = "error"


class LLMQueryValidator:
    """
    Validator che usa LLaMA 3 8B (Groq) per determinare se una query è appropriata.
    Fallback intelligente: Groq → GPT-4o → Pattern-based.
    Implementa comportamenti sicuri e allineati (Bonus #2 e #3).
    """
    
    def __init__(self, groq_api_key: str = None, openai_api_key: str = None):
        """
        Inizializza il validator con fallback intelligente.
        
        Args:
            groq_api_key: Groq API key per LLaMA 3 8B (preferito)
            openai_api_key: OpenAI API key per GPT-4o (fallback)
        """
        # Setup Groq client (prima scelta)
        if groq_api_key is None:
            groq_api_key = os.getenv("GROQ_API_KEY")
        
        if groq_api_key:
            try:
                self.groq_client = Groq(api_key=groq_api_key)
                logger.info("Groq client initialized for LLaMA 3 8B validation")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.groq_client = None
        else:
            self.groq_client = None
            logger.info("No Groq API key found, will try GPT-4o fallback")
        
        # Setup OpenAI client (fallback)
        if openai_api_key is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client available for validation fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
            logger.info("No OpenAI API key found")
        
        # Models configuration
        self.groq_model = "llama-3.1-8b-instant"  # Lightweight model come richiesto
        self.openai_model = "gpt-4o"  # Fallback model
        
        # System prompt per il validation
        self.validation_prompt = """You are a safety validator for a file operations agent. Your job is to classify user queries into categories.

The agent can ONLY help with file operations in a specific directory:
- Listing files
- Reading file contents  
- Writing/creating files
- Deleting files
- Answering questions about file contents and their functionality

APPROVE queries that are:
- File operation requests ("list files", "read example.txt")
- Questions about files or their contents ("what does script.py do?", "what's in config.json?")
- File analysis questions ("analyze hello.py", "what is the purpose of data.csv?")
- File management tasks ("create", "delete", "write")

REJECT queries that are:
- Personal greetings without file context ("hello", "how are you?")
- General programming help not about specific files ("how to write Python?")
- System operations outside the directory ("access /etc/passwd")
- General knowledge questions ("what is Python?")
- Questions about non-file topics ("weather", "news")

IMPORTANT: Questions about what a specific file does (like "cosa fa hello.py?") are APPROVED file analysis queries.

Respond with a JSON object:
{
    "status": "approved" | "rejected_inappropriate" | "rejected_unsafe" | "rejected_off_topic",
    "reason": "Brief explanation of your decision",
    "category": "file_operation" | "information_request" | "inappropriate" | "unsafe" | "off_topic"
}

When in doubt about file-related queries, APPROVE them."""

    async def validate_query(self, query: str) -> Tuple[bool, str, ValidationResult]:
        """
        Valida una query con fallback intelligente: Groq → GPT-4o → Pattern-based.
        
        Args:
            query: Query dell'utente da validare
            
        Returns:
            Tuple (is_valid, explanation, result_type)
        """
        # STEP 1: Prova con LLaMA 3 8B (Groq) - preferito
        if self.groq_client:
            try:
                result = await self._validate_with_groq(query)
                if result:  # Se ha funzionato
                    return result
            except Exception as e:
                logger.warning(f"Groq validation failed: {e}, trying GPT-4o fallback")
        
        # STEP 2: Fallback su GPT-4o se Groq non disponibile ma OpenAI sì
        if self.openai_client:
            try:
                result = await self._validate_with_openai(query)
                if result:  # Se ha funzionato
                    return result
            except Exception as e:
                logger.warning(f"OpenAI validation failed: {e}, falling back to pattern-based")
        
        # STEP 3: Ultimo fallback su pattern-based se entrambe le API non funzionano
        logger.info("Using pattern-based validation as final fallback")
        return self._fallback_validation(query)

    async def _validate_with_groq(self, query: str) -> Optional[Tuple[bool, str, ValidationResult]]:
        """
        Valida usando LLaMA 3 8B via Groq.
        
        Returns:
            None se fallisce, altrimenti il risultato della validazione
        """
        try:
            messages = [
                {"role": "system", "content": self.validation_prompt},
                {"role": "user", "content": f"Validate this query: '{query}'"}
            ]
            
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=messages,
                temperature=0.1,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._process_validation_result(result, "LLaMA 3 8B")
            
        except Exception as e:
            logger.warning(f"Groq validation error: {e}")
            return None

    async def _validate_with_openai(self, query: str) -> Optional[Tuple[bool, str, ValidationResult]]:
        """
        Valida usando GPT-4o come fallback.
        
        Returns:
            None se fallisce, altrimenti il risultato della validazione
        """
        try:
            messages = [
                {"role": "system", "content": self.validation_prompt},
                {"role": "user", "content": f"Validate this query: '{query}'"}
            ]
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                temperature=0.1,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._process_validation_result(result, "GPT-4o")
            
        except Exception as e:
            logger.warning(f"OpenAI validation error: {e}")
            return None

    def _process_validation_result(self, result: Dict[str, Any], model_name: str) -> Tuple[bool, str, ValidationResult]:
        """
        Processa il risultato JSON della validazione da qualsiasi modello.
        
        Args:
            result: Risultato JSON dal modello
            model_name: Nome del modello utilizzato (per logging)
            
        Returns:
            Tuple con risultato validazione
        """
        status = result.get("status", "error")
        reason = result.get("reason", "Unknown validation error")
        
        logger.info(f"Validation by {model_name}: {status} - {reason}")
        
        # Converte il risultato
        if status == "approved":
            return True, reason, ValidationResult.APPROVED
        elif status == "rejected_inappropriate":
            return False, self._format_rejection_message(reason, "inappropriate"), ValidationResult.REJECTED_INAPPROPRIATE
        elif status == "rejected_unsafe":
            return False, self._format_rejection_message(reason, "unsafe"), ValidationResult.REJECTED_UNSAFE
        elif status == "rejected_off_topic":
            return False, self._format_rejection_message(reason, "off_topic"), ValidationResult.REJECTED_OFF_TOPIC
        else:
            return False, "Query validation failed", ValidationResult.ERROR
    
    def _format_rejection_message(self, reason: str, rejection_type: str) -> str:
        """
        Formatta un messaggio di rifiuto user-friendly.
        
        Args:
            reason: Ragione del rifiuto dal modello
            rejection_type: Tipo di rifiuto
            
        Returns:
            Messaggio formattato per l'utente
        """
        base_message = "I am designed to assist only with file operations within a specific directory."
        
        type_messages = {
            "inappropriate": f"Your request appears to be outside my scope. {reason}",
            "unsafe": f"I cannot process requests that might be unsafe. {reason}",
            "off_topic": f"Your question is not related to file operations. {reason}"
        }
        
        specific_message = type_messages.get(rejection_type, reason)
        
        return f"{base_message} {specific_message}\n\nI can help you with:\n- Listing files in the directory\n- Reading file contents\n- Writing or creating files\n- Deleting files\n- Answering questions about file contents"
    
    def _fallback_validation(self, query: str) -> Tuple[bool, str, ValidationResult]:
        """
        Validazione di fallback pattern-based se LLM non disponibile.
        """
        query_lower = query.lower().strip()
        
        # Pattern inappropriati semplici
        inappropriate_patterns = [
            "hello", "hi", "how are you", "weather", "news", "politics",
            "relationship", "love", "money", "health", "recipe", "cooking",
            "sport", "movie", "music"
        ]
        
        # Pattern appropriati per file operations  
        file_patterns = [
            "file", "read", "write", "list", "delete", "create", "content", 
            "directory", "folder", "document", "text", ".py", ".txt", ".json",
            ".csv", ".md", "cosa fa", "what does", "analyze", "analizza"
        ]
        
        # Pattern per analisi file (sempre approvate)
        file_analysis_patterns = [
            "cosa fa", "what does", "che cosa fa", "what is in", "analyze",
            "analizza", "summarize", "riassumi", "explain", "spiega"
        ]
        
        # Controlla pattern di analisi file (priorità alta)
        if any(pattern in query_lower for pattern in file_analysis_patterns):
            return True, "Query is asking about file analysis/content", ValidationResult.APPROVED
        
        # Controlla se contiene file operations keywords (priorità alta)
        file_operation_keywords = ["read", "write", "list", "delete", "create", "analyze"]
        if any(keyword in query_lower for keyword in file_operation_keywords):
            return True, "Query contains file operation keywords", ValidationResult.APPROVED
        
        # Controlla se contiene estensioni di file (priorità alta)
        if "." in query_lower and any(ext in query_lower for ext in [".py", ".txt", ".json", ".csv", ".md", ".log"]):
            return True, "Query mentions specific file", ValidationResult.APPROVED
        
        # Controlla pattern inappropriati (solo se non è già stata approvata)
        if any(pattern in query_lower for pattern in inappropriate_patterns):
            # Ma ignora se la query contiene anche pattern di file
            if not any(pattern in query_lower for pattern in file_patterns):
                return False, self._format_rejection_message(
                    "This appears to be a general question outside my file operations scope.", 
                    "off_topic"
                ), ValidationResult.REJECTED_OFF_TOPIC
        
        # Controlla pattern appropriati
        if any(pattern in query_lower for pattern in file_patterns):
            return True, "Query appears to be file-related", ValidationResult.APPROVED
        
        # Default: rifiuta se ambiguo
        return False, self._format_rejection_message(
            "Your request is too generic. Please specify what you want to do with files.", 
            "inappropriate"
        ), ValidationResult.REJECTED_INAPPROPRIATE
    
    def get_model_info(self) -> Dict[str, Any]:
        """Restituisce informazioni sul modello utilizzato."""
        return {
            "model": self.groq_model,
            "provider": "Groq",
            "purpose": "Query validation and safety filtering",
            "available": self.groq_client is not None
        } 