"""
LLM-powered File Operations Agent using GPT-4o.
Implements ReAct reasoning pattern with intelligent tool orchestration.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from .llm_validator import LLMQueryValidator, ValidationResult
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class LLMFileAgent:
    """
    Agente principale, che usa GPT-4o per reasoning e tool orchestration.
    Implementa pattern ReAct (Reasoning and Acting) come richiesto dall'assignment.
    """
    def __init__(self, base_directory: str, openai_api_key: str = None, groq_api_key: str = None, verbose: bool = False):
        """
        Inizializza l'agente LLM.
        
        Args:
            base_directory: Directory base per le operazioni sui file
            openai_api_key: OpenAI API key per GPT-4o
            groq_api_key: Groq API key per LLaMA 3 8B validation
            verbose: Flag per logging dettagliato
        """
        self.base_directory = base_directory
        self.verbose = verbose
        
        # Inizializza OpenAI client per GPT-4o
        if openai_api_key is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.main_model = "gpt-4o"
        
        # Inizializza tool registry con API key per answer_question_about_files
        self.tool_registry = ToolRegistry(base_directory, openai_api_key)
        
        # Inizializza LLM validator per prompt rejection (Bonus #2 e #3)
        # Passa entrambe le API keys per fallback intelligente: Groq → GPT-4o → Pattern-based
        self.validator = LLMQueryValidator(groq_api_key, openai_api_key)
        
        # Conversation history per context management
        self.conversation_history = []
        
        # System prompt per GPT-4o
        self.system_prompt = self._build_system_prompt()
        
        if verbose:
            logger.info(f"LLM Agent initialized for directory: {base_directory}")
            logger.info(f"Main model: {self.main_model}")
            
            # Mostra status validation con nuovo fallback
            if self.validator.groq_client:
                validator_status = "LLaMA 3 8B (Groq) + GPT-4o fallback + pattern fallback"
            elif self.validator.openai_client:
                validator_status = "GPT-4o validation + pattern fallback (no Groq)"
            else:
                validator_status = "Pattern-based only (no API keys)"
            
            logger.info(f"Validator chain: {validator_status}")
    
    def _build_system_prompt(self) -> str:
        """Costruisce il system prompt per l'agente LLM con focus sui tool."""
        return f"""You are an intelligent file operations agent with access to powerful tools.

**CRITICAL REQUIREMENT: You MUST use tools for ALL file-related operations.**

**Your Role:**
- You help users manage files in the directory: {self.base_directory}
- You can perform CRUD operations and answer intelligent questions about files
- You use a ReAct (Reasoning-Action-Observation) approach with sequential tool orchestration

**MANDATORY TOOL USAGE RULES:**
- For ANY file listing request → MUST use list_files() tool
- For ANY file reading request → MUST use read_file(filename) tool  
- For ANY file creation/writing → MUST use write_file(filename, content, mode) tool
- For ANY file deletion → MUST use delete_file(filename) tool
- For ANY file analysis questions → MUST use answer_question_about_files(query) tool
- For general file questions → MUST use list_files() first, then appropriate tools

**Examples of MANDATORY tool usage:**
- "list files" → MUST call list_files()
- "read example.txt" → MUST call read_file("example.txt")
- "what files are here?" → MUST call list_files()
- "create test.txt" → MUST call write_file("test.txt", content, "w")
- "delete old.log" → MUST call delete_file("old.log")
- "what's the largest file?" → MUST call answer_question_about_files("what's the largest file?")
- "what does hello.py do?" → MUST call answer_question_about_files("what does hello.py do?")
- "cosa fa config.json?" → MUST call answer_question_about_files("cosa fa config.json?")

**Sequential Multi-Tool Orchestration:**
For complex requests, use multiple tools in sequence:
1. Use list_files() to get overview
2. Use read_file() for specific content
3. Use answer_question_about_files() for analysis
4. Use write_file() or delete_file() for modifications

**Example Multi-Step Workflow:**
If user asks "read the most recently modified file":
1. MUST use list_files() to get all files with metadata
2. Analyze the modification dates to identify the most recent file
3. MUST use read_file(filename) to read that specific file
4. Provide the content to the user

**NEVER respond to file-related requests without using appropriate tools.**

**Only respond without tools for:**
- Help/documentation requests about your capabilities
- Questions about your functionality
- Non-file-related questions

Working Directory: {self.base_directory}
Available Tools: list_files, read_file, write_file, delete_file, answer_question_about_files

Remember: Tool usage is MANDATORY for all file operations. Always use tools first, then provide explanations based on the results."""

    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Processa una query utente usando il pattern ReAct con GPT-4o.
        
        Args:
            query: Query dell'utente
            
        Returns:
            Dict con risultato dell'elaborazione
        """
        try:
            # STEP 1: Validation con LLaMA 3 8B (Bonus #2 e #3)
            is_valid, validation_message, validation_result = await self.validator.validate_query(query)
            
            if not is_valid:
                return {
                    "success": False,
                    "message": validation_message,
                    "validation_result": validation_result.value,
                    "reasoning": "Query rejected by safety validator"
                }
            
            # STEP 2: ReAct reasoning con GPT-4o
            if self.verbose:
                logger.info(f"Processing query with GPT-4o: {query}")
            
            response = await self._execute_react_loop(query)
            
            # Aggiorna conversation history
            self.conversation_history.append({
                "user_query": query,
                "response": response,
                "validation": validation_result.value
            })
            
            return {
                "success": True,
                "message": response,
                "validation_result": validation_result.value,
                "reasoning": "Processed successfully by GPT-4o"
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            
            # Ultimate fallback - prova a dare una risposta utile anche in caso di errore grave
            fallback_message = f"I encountered some technical difficulties, but let me try to help you anyway. "
            
            # Analizza la query per dare suggerimenti specifici
            query_lower = query.lower()
            if "list" in query_lower or "files" in query_lower:
                fallback_message += "You asked about listing files. Try: 'python -c \"import os; print(os.listdir('.'))\"'"
            elif "read" in query_lower:
                fallback_message += "You asked to read a file. Try opening the file directly with a text editor."
            elif "write" in query_lower or "create" in query_lower:
                fallback_message += "You asked to write/create a file. Try using a text editor or basic file commands."
            elif "delete" in query_lower:
                fallback_message += "You asked to delete a file. Please use file manager or command line carefully."
            else:
                fallback_message += "Please try rephrasing your request or use basic file operations."
            
            fallback_message += f"\n\nTechnical error: {str(e)}"
            
            return {
                "success": False,
                "message": fallback_message,
                "validation_result": "error_with_fallback",
                "reasoning": f"Provided fallback assistance despite error: {str(e)}"
            }
    
    async def _execute_react_loop(self, query: str) -> str:
        """
    Esegue un loop dove GPT-4o:

    - Riceve il messaggio dell'utente

    - Decide se servono uno o più tool

    - Chiama i tool in sequenza (via ToolRegistry)

    -Riceve i risultati e continua il ragionamento

È qui che avviene il pattern ReAct: reasoning, action (tool), observation (output del tool)...
        
        Args:
            query: Query dell'utente
            
        Returns:
            Risposta finale dell'agente
        """
        # Prepara la conversazione con context
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Aggiungi context dalla conversation history (ultimi 3 scambi)
        recent_history = self.conversation_history[-3:] if self.conversation_history else []
        for entry in recent_history:
            messages.append({"role": "user", "content": entry["user_query"]})
            messages.append({"role": "assistant", "content": entry["response"]})
        
        # Aggiungi la query attuale
        messages.append({"role": "user", "content": query})
        
        # Definisci le funzioni tool per GPT-4o
        tools = self._build_openai_tools()
        
        # ReAct loop con sequential tool orchestration
        max_iterations = 5 #Dopo max 5 giri, fornisce una risposta finale
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            if self.verbose:
                logger.info(f"ReAct iteration {iteration}/{max_iterations}")
            
            # Chiamata a GPT-4o per reasoning e tool selection
            response = self.openai_client.chat.completions.create(
                model=self.main_model,
                messages=messages, #messages: lista dei messaggi della conversazione
                tools=tools, #tools: lista dei tool disponibili
                tool_choice="auto", #tool_choice: auto, required, none
                temperature=0.1, # temperature tra 0.1 e 0.3: affidabile, poco creativo, ottimo per task strutturati
                max_tokens=1500 # max_tokens: dimensione della risposta (1500 è un buon compromesso)
            )
            
            assistant_message = response.choices[0].message
            
            # Se GPT-4o vuole usare tool
            if assistant_message.tool_calls:
                if self.verbose:
                    logger.info(f"GPT-4o requested {len(assistant_message.tool_calls)} tool calls")
                
                # Aggiungi il messaggio dell'assistant alla conversazione
                messages.append(assistant_message)
                
                # Eseguire le chiamate ai tool (chiamata a GPT-4o per reasoning e tool selection)
                all_tools_successful = True
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    if self.verbose:
                        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    # Eseguire il tool
                    try:
                        tool_result = self.tool_registry.execute_tool(tool_name, **tool_args) #tool_registry: oggetto che gestisce i tool
                        tool_result_str = str(tool_result) if tool_result is not None else "Operation completed successfully" #tool_result: risultato dell'esecuzione del tool
                    except Exception as e:
                        tool_result_str = f"Error executing {tool_name}: {str(e)}" #tool_result_str: stringa che rappresenta il risultato dell'esecuzione del tool
                        all_tools_successful = False
                    
                    # Aggiungi il risultato del tool alla conversazione
                    messages.append({
                        "role": "tool",
                        "content": tool_result_str,
                        "tool_call_id": tool_call.id
                    })
                
                # Se ci sono stati errori nei tool, continua comunque per permettere recovery
                if not all_tools_successful:
                    if self.verbose:
                        logger.warning("Some tools failed, but continuing to allow recovery and fallback")
                    # Non interrompere il loop - lascia che GPT-4o tenti recovery o fallback
                    
                # Continuare il loop per permettere sequential reasoning
                continue
                
            else:
                # GPT-4o ha risposto senza tool - verifica se doveva usarli
                if self._should_use_tools(query, messages):
                    if self.verbose:
                        logger.warning("GPT-4o responded without tools for file operation - forcing tool usage")
                    
                    # Aggiungi il messaggio dell'assistant
                    messages.append(assistant_message)
                    
                    # Forza l'uso di tool con un prompt diretto
                    messages.append({
                        "role": "user",
                        "content": "You MUST use the appropriate tools to complete this file operation. Please use the required tools now."
                    })
                    
                    # Riprova se c'è ancora un'iterazione disponibile
                    if iteration < max_iterations:
                        continue
                    else:
                        # Fallback finale: prova a dare una risposta utile anche senza tool perfetti
                        if self.verbose:
                            logger.warning("Max iterations reached without proper tool usage - providing fallback response")
                        
                        # Genera una risposta che ammette il problema ma prova ad aiutare
                        fallback_message = assistant_message.content + "\n\n[Note: I wasn't able to use the appropriate tools for this file operation, but I've provided the best response I can based on your request.]"
                        return fallback_message
                else:
                    # Query non-file related, ok rispondere direttamente
                    return assistant_message.content
        
        # Se siamo arrivati qui, abbiamo eseguito tool - genera risposta finale che includa i risultati
        if self.verbose:
            logger.info("Generating final response with tool results")
        
        try:
            messages.append({
                "role": "user", 
                "content": "Based on the tool results above, provide a complete response to my original question. If you read a file, include its content. If you analyzed files, include your analysis. Be specific and include all relevant information from the tool outputs."
            })
            
            final_response = self.openai_client.chat.completions.create(
                model=self.main_model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            return final_response.choices[0].message.content
            
        except Exception as e:
            # Fallback se la chiamata finale fallisce
            if self.verbose:
                logger.error(f"Final synthesis failed: {e}")
            
            return f"I encountered some difficulties processing your request, but I tried my best to help. The issue was: {str(e)}. Please try rephrasing your request or check if the files/directory are accessible."
    
    def _build_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Costruisce la definizione dei tool per OpenAI function calling.
        
        Returns:
            Lista di tool definitions per OpenAI API
        """
        tools = []
        
        # list_files tool
        tools.append({
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List all files in the working directory with metadata including name, size, and modification date",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        })
        
        # read_file tool
        tools.append({
            "type": "function", 
            "function": {
                "name": "read_file",
                "description": "Read the complete content of a specific file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to read"
                        }
                    },
                    "required": ["filename"]
                }
            }
        })
        
        # write_file tool
        tools.append({
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file (create new or overwrite existing)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["w", "a"],
                            "default": "w",
                            "description": "Write mode: 'w' to overwrite, 'a' to append"
                        }
                    },
                    "required": ["filename", "content"]
                }
            }
        })
        
        # delete_file tool
        tools.append({
            "type": "function",
            "function": {
                "name": "delete_file", 
                "description": "Delete a file from the working directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to delete"
                        }
                    },
                    "required": ["filename"]
                }
            }
        })
        
        # answer_question_about_files tool
        tools.append({
            "type": "function",
            "function": {
                "name": "answer_question_about_files",
                "description": "Answer intelligent questions about files by analyzing their contents, metadata, and patterns. Use this for questions like 'What does script.py do?', 'What is the purpose of config.json?', or general file analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Question about the files (e.g., 'What does hello.py do?', 'What is the largest file?', 'Which files contain Python code?', 'What is the purpose of config.json?')"
                        }
                    },
                    "required": ["query"]
                }
            }
        })
        
        return tools
    
    def _should_use_tools(self, original_query: str, messages: List[Dict[str, Any]]) -> bool:
        """
        Determina se la query richiede l'uso di tool per operazioni sui file.
        
        Args:
            original_query: Query originale dell'utente
            messages: Cronologia della conversazione
            
        Returns:
            True se dovrebbero essere usati tool, False altrimenti
        """
        # Keywords che indicano operazioni sui file
        file_operation_keywords = [
            "file", "files", "list", "read", "write", "create", "delete", "remove",
            "directory", "folder", "content", "text", "data", "json", "csv", "log",
            "size", "largest", "smallest", "modified", "recent", "analyze", "find",
            "search", "contains", "backup", "copy", "save", "load", "open"
        ]
        
        # Keywords che indicano richieste di aiuto/informazioni (non file operations)
        help_keywords = [
            "help", "what can you do", "how do you work", "capabilities", "what are you",
            "who are you", "explain", "describe yourself", "what is", "how to use"
        ]
        
        query_lower = original_query.lower()
        
        # Se contiene keywords di aiuto, non servono tool
        if any(keyword in query_lower for keyword in help_keywords):
            return False
        
        # Se contiene keywords di file operations, servono tool
        if any(keyword in query_lower for keyword in file_operation_keywords):
            return True
        
        # Se la query è molto corta e generica, probabilmente non serve tool
        if len(original_query.strip()) < 10:
            return False
        
        # Default: se siamo in dubbio e la query non è chiaramente di aiuto, probabilmente serve tool
        return True
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Restituisce la cronologia della conversazione."""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Pulisce la cronologia della conversazione."""
        self.conversation_history.clear()
        if self.verbose:
            logger.info("Conversation history cleared")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Restituisce informazioni sull'agente e sui modelli utilizzati.
        
        Returns:
            Dict con informazioni sull'agente
        """
        return {
            "agent_type": "LLM-powered File Operations Agent",
            "main_model": {
                "name": self.main_model,
                "provider": "OpenAI",
                "purpose": "Reasoning, planning, and tool orchestration"
            },
            "validator_model": self.validator.get_model_info(),
            "base_directory": self.base_directory,
            "available_tools": list(self.tool_registry.list_tools().keys()),
            "conversation_length": len(self.conversation_history),
            "capabilities": [
                "Natural language understanding",
                "ReAct reasoning pattern", 
                "Intelligent tool orchestration",
                "Safety validation with lightweight model",
                "Context-aware conversations"
            ]
        }
    
    def get_help(self) -> str:
        """Restituisce un messaggio di aiuto per l'utente."""
        return """🤖 LLM File Operations Agent

I'm an AI assistant powered by GPT-4o, specialized in file operations. I can understand natural language and intelligently use tools to help you manage files.

**What I can do:**
• **List files**: "Show me all files" or "What files are in the directory?"
• **Read files**: "Read the content of example.txt" or "What's in the Python file?"
• **Write files**: "Create a file called notes.txt with content 'Hello World'"
• **Delete files**: "Delete the file old_data.csv"
• **Intelligent analysis**: "What's the largest file?" or "Which files contain code?"

**Key features:**
• Natural language understanding (no need for exact commands)
• Multi-step reasoning (I can combine multiple operations)
• Safety validation (inappropriate requests are filtered out)
• Context awareness (I remember our conversation)

**Examples:**
• "Find the file that was modified most recently and show me its content"
• "Create a summary of all text files in the directory"
• "Delete all files that are smaller than 100 bytes"

Just ask me what you'd like to do with your files in natural language! 🚀
        """ 