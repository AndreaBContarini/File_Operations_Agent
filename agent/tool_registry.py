"""
Registry centrale per tutti i tool disponibili.
Fornisce interfaccia unificata per l'esecuzione di tool con gestione degli errori.
"""
from typing import Dict, Any, Callable, Optional, List
import logging
from pathlib import Path

# Import dei tool
from tools.list_files import list_files
from tools.read_file import read_file
from tools.write_file import write_file
from tools.delete_file import delete_file
from tools.answer_question_about_files import answer_question_about_files

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry centrale per la gestione e l'esecuzione dei tool.
    Fornisce interfaccia unificata con validazione dei parametri e error handling.
    """
    
    def __init__(self, base_directory: str, openai_api_key: Optional[str] = None):
        """
        Inizializza il registry con la directory base e API key.
        
        Args:
            base_directory: Directory base per tutte le operazioni sui file
            openai_api_key: API key OpenAI per il tool answer_question_about_files
        """
        self.base_directory = str(Path(base_directory).resolve())
        self.openai_api_key = openai_api_key
        
        # Registry dei tool con le relative funzioni
        self._tools: Dict[str, Callable] = {
            # Wrapper function: adatta l'interfaccia del tool grezzo per integrarlo con il sistema
            # Qui aggiungiamo gestione degli errori, validazioni e passaggio automatico di parametri come la directory o API key
            "list_files": self._wrap_list_files,
            "read_file": self._wrap_read_file,
            "write_file": self._wrap_write_file,
            "delete_file": self._wrap_delete_file,
            "answer_question_about_files": self._wrap_answer_question
        }
        
        logger.info(f"ToolRegistry initialized with {len(self._tools)} tools for directory: {self.base_directory}")
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Esegue un tool specifico con i parametri forniti.
        
        Args:
            tool_name: Nome del tool da eseguire
            **kwargs: Parametri per il tool
            
        Returns:
            Risultato dell'esecuzione del tool
            
        Raises:
            ValueError: Se il tool non esiste
            Exception: Per errori durante l'esecuzione
        """
        if tool_name not in self._tools:
            available_tools = ", ".join(self._tools.keys())
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")
        
        try:
            logger.debug(f"Executing tool: {tool_name} with args: {kwargs}")
            result = self._tools[tool_name](**kwargs)
            logger.debug(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    def list_tools(self) -> Dict[str, str]:
        """
        Restituisce la lista di tutti i tool disponibili con le loro descrizioni.
        
        Returns:
            Dict con nome tool -> descrizione
        """
        return {
            "list_files": "Lista tutti i file nella directory con metadati",
            "read_file": "Legge il contenuto completo di un file",
            "write_file": "Scrive contenuto in un file (crea o sovrascrive)",
            "delete_file": "Elimina un file dalla directory",
            "answer_question_about_files": "Risponde a domande intelligenti sui file"
        }
    
    def get_tools_description(self) -> str:
        """
        Restituisce una descrizione formattata di tutti i tool.
        
        Returns:
            Stringa con descrizione di tutti i tool
        """
        tools_info = []
        for name, description in self.list_tools().items():
            tools_info.append(f"• {name}: {description}")
        return "\n".join(tools_info)
    
    def tool_exists(self, tool_name: str) -> bool:
        """
        Verifica se un tool esiste nel registry.
        
        Args:
            tool_name: Nome del tool da verificare
            
        Returns:
            True se il tool esiste
        """
        return tool_name in self._tools
    
    def get_base_directory(self) -> str:
        """Restituisce la directory base configurata."""
        return self.base_directory
    
    # Wrapper methods per i tool individuali
    
    def _wrap_list_files(self) -> Optional[List[Dict[str, Any]]]:
        """Wrapper per list_files tool."""
        try:
            return list_files(self.base_directory)
        except Exception as e:
            logger.error(f"Error in list_files: {e}")
            raise
    
    def _wrap_read_file(self, filename: str) -> str:
        """
        Wrapper per read_file tool.
        
        Args:
            filename: Nome del file da leggere
            
        Returns:
            Contenuto del file
        """
        if not filename:
            raise ValueError("filename parameter is required")
        
        try:
            return read_file(filename, self.base_directory)
        except (FileNotFoundError, ValueError) as e:
            # Questi sono errori "expected" (file non trovato, binario, etc.) - non loggarli come ERROR
            logger.debug(f"Expected error reading file {filename}: {e}")
            raise
        except Exception as e:
            # Solo errori inaspettati vengono loggati come ERROR
            logger.error(f"Unexpected error reading file {filename}: {e}")
            raise
    
    def _wrap_write_file(self, filename: str, content: str, mode: str = "w") -> bool:
        """
        Wrapper per write_file tool.
        
        Args:
            filename: Nome del file da scrivere
            content: Contenuto da scrivere
            mode: Modalità di scrittura ("w" o "a")
            
        Returns:
            True se l'operazione è riuscita
        """
        if not filename:
            raise ValueError("filename parameter is required")
        if content is None:
            raise ValueError("content parameter is required")
        if mode not in ["w", "a"]:
            raise ValueError("mode must be 'w' or 'a'")
        
        try:
            return write_file(filename, content, self.base_directory, mode)
        except Exception as e:
            logger.error(f"Error writing file {filename}: {e}")
            raise
    
    def _wrap_delete_file(self, filename: str) -> bool:
        """
        Wrapper per delete_file tool.
        
        Args:
            filename: Nome del file da eliminare
            
        Returns:
            True se l'operazione è riuscita
        """
        if not filename:
            raise ValueError("filename parameter is required")
        
        try:
            return delete_file(filename, self.base_directory)
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            raise
    
    def _wrap_answer_question(self, query: str) -> str:
        """
        Wrapper per answer_question_about_files tool.
        
        Args:
            query: Domanda sui file
            
        Returns:
            Risposta alla domanda
        """
        if not query:
            raise ValueError("query parameter is required")
        
        try:
            return answer_question_about_files(self.base_directory, query, self.openai_api_key)
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise 