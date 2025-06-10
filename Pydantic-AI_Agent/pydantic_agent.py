"""
Hybrid agent using GPT-4o for file operations and Groq for query validation.

Architecture:
- Groq llama-3.1-8b-instant: User query validation (optional, if APIs are provided...theyy're free!)
- GPT-4o: File operations with Pydantic-AI (required)
"""
import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.groq import GroqProvider

try:
    from .dependencies import AgentDependencies
    from .models import AgentResponse
except ImportError:
    from dependencies import AgentDependencies
    from models import AgentResponse

# Import original tools for reuse
import sys
sys.path.append(str(Path(__file__).parent.parent))
# Import tools
from tools.list_files import list_files
from tools.read_file import read_file
from tools.write_file import write_file
from tools.delete_file import delete_file
from tools.answer_question_about_files import answer_question_about_files

logger = logging.getLogger(__name__)


class PydanticFileAgent:
    """
    Hybrid agent for file operations.
    
    Uses two LLMs with different functions:
    - Groq llama-3.1-8b-instant: User query validation and preprocessing (optional)
    - GPT-4o: File operations with advanced reasoning (required)
    """
    
    def __init__(
        self, 
        base_directory: str, 
        openai_api_key: str,
        groq_api_key: Optional[str] = None, 
        verbose: bool = False # It is used to print the logs of the agent
    ):
        """
        Initialize the hybrid agent.
        
        Args:
            base_directory: Base directory for file operations (fixed)
            openai_api_key: API key for OpenAI GPT-4o (required)
            groq_api_key: API key for Groq llama-3.1-8b-instant (optional)
            verbose: Flag for detailed logging
        """
        self.base_directory = base_directory
        self.verbose = verbose
        self.openai_api_key = openai_api_key
        self.groq_api_key = groq_api_key
        
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for file operations")
        
        # Create dependencies for dependency injection
        self.dependencies = AgentDependencies(
            base_directory=base_directory,
            openai_api_key=openai_api_key,
            verbose=verbose
        )
        
        # Initialize GPT-4o agent for file operations
        openai_provider = OpenAIProvider(api_key=openai_api_key)
        openai_model = OpenAIModel("gpt-4o", provider=openai_provider)
        
        self.file_operations_agent = Agent(
            model=openai_model,
            deps_type=AgentDependencies,
            result_type=AgentResponse,
            system_prompt=self._build_file_operations_prompt()
        )
        
        # Initialize Groq agent for validation (optional) 
        # Note: Simplified validation without complex tools to avoid Groq tool calling issues
        self.validation_agent = None
        if groq_api_key:
            try:
                groq_provider = GroqProvider(api_key=groq_api_key)
                groq_model = GroqModel("llama-3.1-8b-instant", provider=groq_provider)
                
                # Use simple string response instead of complex structured output
                self.validation_agent = Agent(
                    model=groq_model,
                    system_prompt=self._build_simple_validation_prompt()
                )
                
                if verbose: # It is used to print the logs of the agent
                    logger.info("Validation agent (Groq) initialized successfully")
            except Exception as e: # it means that the Groq API key is not valid
                logger.warning(f"Failed to initialize validation agent: {e}")
                self.validation_agent = None
        
        # Register tools for file operations
        self._register_file_tools()
        
        if verbose:
            logger.info(f"Hybrid PydanticFileAgent initialized")
            logger.info(f"Directory: {base_directory}")
            logger.info(f"OpenAI GPT-4o: ✅ Ready for file operations")
            logger.info(f"Groq validation: {'✅ Enabled' if self.validation_agent else '❌ Disabled'}")
    
    def _build_simple_validation_prompt(self) -> str:
        """Simple validation prompt for Groq without complex tool calling."""
        
        return """You are a security validator for file operations. Analyze user queries and respond with ONLY one of these words:

SAFE - if the query is safe for file operations (list, read, write, delete normal files, analyze, ask about files)
DANGEROUS - if the query contains system commands, path traversal, or dangerous operations

Examples:
"list files" → SAFE
"read config.json" → SAFE  
"write hello to test.txt" → SAFE
"delete temp.log" → SAFE
"what does hello.py do?" → SAFE
"cosa fa config.json?" → SAFE
"analyze the files" → SAFE
"rm -rf /" → DANGEROUS
"format C:" → DANGEROUS
"cat /etc/passwd" → DANGEROUS
"../../../etc/passwd" → DANGEROUS

Questions about file content and functionality are SAFE.

Respond with ONLY the word SAFE or DANGEROUS."""

    def _build_file_operations_prompt(self) -> str:
        """Prompt for GPT-4o file operations agent with mandatory tool usage."""
        return f"""You are an expert file operations agent with access to powerful tools.

**CRITICAL REQUIREMENT: You MUST use tools for ALL file-related operations.**

**Working Directory:** {self.base_directory}

**MANDATORY TOOL USAGE RULES:**
- For ANY file listing request → MUST use list_files_tool()
- For ANY file reading request → MUST use read_file_tool(filename)  
- For ANY file creation/writing → MUST use write_file_tool(filename, content, mode)
- For ANY file deletion → MUST use delete_file_tool(filename)
- For ANY file analysis questions → MUST use answer_question_tool(query)
- For general file questions → MUST use list_files_tool() first, then appropriate tools

**Examples of MANDATORY tool usage:**
- "list files" → MUST call list_files_tool()
- "read example.txt" → MUST call read_file_tool("example.txt")
- "what files are here?" → MUST call list_files_tool()
- "create test.txt" → MUST call write_file_tool("test.txt", content, "w")
- "delete old.log" → MUST call delete_file_tool("old.log")
- "what's the largest file?" → MUST call answer_question_tool("what's the largest file?")
- "what does hello.py do?" → MUST call answer_question_tool("what does hello.py do?")
- "what can you tell me about config.json file?" → MUST call answer_question_tool("what can you tell me about config.json file?")

**Multi-Step Tool Orchestration:**
For complex requests, use multiple tools in sequence:
1. Use list_files_tool() to get file overview
2. Use read_file_tool() for specific content
3. Use answer_question_tool() for analysis
4. Use write_file_tool() or delete_file_tool() for modifications

**Operational Process:**
1. Analyze the user's request and identify required tools
2. Plan the sequence of necessary tool operations
3. Execute tools in logical order (MANDATORY for file operations)
4. Provide detailed feedback based on tool results

**Guidelines:**
- ALWAYS use appropriate tools for file operations
- Never assume file existence without using list_files_tool() first
- For complex tasks, use multiple tools in sequence
- Always explain your reasoning and tool selection
- Stay focused only on file operations
- ALWAYS include actual file content when reading files
- Provide complete, actionable responses with structured output

**IMPORTANT for list_files operations:**
- When listing files, you MUST show all file names clearly in the message
- Always populate the 'files' field with the complete list from the tool result
- Format the message to include each file name and size in a readable list
- Do NOT just say "11 files found" - show ALL the actual file names

**NEVER respond to file-related requests without using appropriate tools.**

**Only respond without tools for:**
- Help/documentation requests about your capabilities
- Questions about your functionality
- Non-file-related questions

Your response must always be structured as AgentResponse with:
- success: bool (operation outcome)
- message: str (human-readable description including ALL file names when listing, file content when reading files)
- type: str (operation type: "list_files", "read_file", "write_file", "delete_file", "analysis")
- files: populate this field when listing files with the complete tool result
- file_content: populate this field when reading files with the actual content
- type: str (operation type performed)
- reasoning: str (explanation of the process and tools used)
- file_content: str (MANDATORY: actual file content when reading files)
- files: list (file list when listing files)
- analysis_result: str (analysis results when using answer_question_tool)

**CRITICAL OUTPUT REQUIREMENTS:**
- When reading a file: ALWAYS populate file_content field with the actual content
- When listing files: ALWAYS populate files field with the file list
- When analyzing files: ALWAYS populate analysis_result field with the analysis
- Message should include a summary but file_content should contain the full content

IMPORTANT: Tool usage is MANDATORY for all file operations. Always use tools first, then provide explanations based on the results."""

    def _register_file_tools(self):
        """
        Registra i tool usando i decoratori nativi di Pydantic-AI.
        
        Sostituisce il custom ToolRegistry con tool definition nativi,
        che supportano validazione automatica e error handling.
        """
        
        
        @self.file_operations_agent.tool # Decorator for the tool (from Pydantic-AI); it is used to register the tool in the agent
        async def list_files_tool(ctx: RunContext[AgentDependencies]) -> List[Dict[str, Any]]:
            """
            Lista tutti i file nella directory di lavoro con metadati dettagliati.
            
            Returns:
                Lista di dizionari con informazioni sui file (nome, dimensione, data modifica)
            
            Note: 
            async def: definisce una funzione asincrona.
            All’interno di una funzione async, si può usare la chiave await 
            per 'aspettare' il risultato di un’altra funzione asincrona.
            """
            try:
                if ctx.deps.verbose:
                    logger.info("Executing list_files tool")
                    
                result = list_files(ctx.deps.base_directory)
                
                if ctx.deps.verbose:
                    logger.info(f"Found {len(result) if result else 0} files")
                    
                return result or []
                
            except Exception as e:
                logger.error(f"Error in list_files_tool: {e}")
                raise
        
        @self.file_operations_agent.tool
        async def read_file_tool(
            ctx: RunContext[AgentDependencies], 
            filename: str, 
            encoding: str = 'utf-8'
        ) -> str:
            """
            Read the complete content of a specific file.
            
            Args:
                filename: Name of the file to read
                encoding: File encoding (default: utf-8)
                
            Returns:
                File content as string
            """
            try:
                if ctx.deps.verbose:
                    logger.info(f"Executing read_file tool for: {filename}")
                    
                content = read_file(filename, ctx.deps.base_directory, encoding)
                
                if ctx.deps.verbose:
                    logger.info(f"Successfully read file {filename} ({len(content)} characters)")
                    
                return content
                
            except Exception as e: # Se succede un errore di tipo Exception (cioè praticamente qualsiasi errore), salvalo nella variabile e
                logger.error(f"Error in read_file_tool for {filename}: {e}")
                raise Exception(f"Failed to read file {filename}: {str(e)}")
        
        @self.file_operations_agent.tool
        async def write_file_tool(
            ctx: RunContext[AgentDependencies],
            filename: str,
            content: str,
            mode: str = 'w',
            encoding: str = 'utf-8'
        ) -> bool:
            """
            Write content to a file (create or overwrite).
            
            Args:
                filename: Name of the file to write
                content: Content to write to the file
                mode: Write mode ('w' for overwrite, 'a' for append)
                encoding: File encoding (default: utf-8)
                
            Returns:
                True if operation succeeds
            """
            try:
                if ctx.deps.verbose:
                    logger.info(f"Executing write_file tool for: {filename} (mode: {mode})")
                    
                success = write_file(filename, content, ctx.deps.base_directory, mode, encoding)
                
                if ctx.deps.verbose:
                    logger.info(f"File {filename} written successfully: {success}")
                    
                return success
                
            except Exception as e:
                logger.error(f"Error in write_file_tool for {filename}: {e}")
                raise Exception(f"Failed to write file {filename}: {str(e)}")
        
        @self.file_operations_agent.tool  
        async def delete_file_tool(
            ctx: RunContext[AgentDependencies],
            filename: str
        ) -> bool:
            """
            Delete a file from the working directory.
            
            Args:
                filename: Name of the file to delete
                
            Returns:
                True if operation succeeds
            """
            try:
                if ctx.deps.verbose:
                    logger.info(f"Executing delete_file tool for: {filename}")
                    
                success = delete_file(filename, ctx.deps.base_directory)
                
                if ctx.deps.verbose:
                    logger.info(f"File {filename} deleted successfully: {success}")
                    
                return success
                
            except Exception as e:
                logger.error(f"Error in delete_file_tool for {filename}: {e}")
                raise Exception(f"Failed to delete file {filename}: {str(e)}")
        
        @self.file_operations_agent.tool
        async def answer_question_tool(
            ctx: RunContext[AgentDependencies], # ctx è il contesto di esecuzione che contiene tutte le dipendenze e configurazioni necessarie per l'agente
            query: str # domanda dell'utente
        ) -> str:
            """
            Answer intelligent questions about files by analyzing metadata and contents.
            
            Args:
                query: Question about the files
                
            Returns:
                Answer to the question
            """
            try:
                if ctx.deps.verbose: # se verbose è True, stampa il log
                    logger.info(f"Executing answer_question tool with query: {query}")
                    
                answer = answer_question_about_files(ctx.deps.base_directory, query, ctx.deps.openai_api_key)
                
                if ctx.deps.verbose:
                    logger.info(f"Generated answer for file question")
                    
                return answer
                
            except Exception as e:
                logger.error(f"Error in answer_question_tool: {e}")
                raise Exception(f"Failed to answer question: {str(e)}")
    
    async def _validate_query(self, query: str) -> tuple[bool, str]:
        """
        Validate user query using Groq (if available).
        
        Args:
            query: User query to validate
            
        Returns:
            tuple: (is_valid, sanitized_query)
        """
        if not self.validation_agent:
            # No validation available, proceed directly
            return True, query
            
        try:
            if self.verbose:
                logger.info(f"Validating query with Groq: {query}")
                
            result = await self.validation_agent.run(query)
            validation_response = result.data.strip().upper()
            
            is_safe = validation_response == "SAFE"
            
            if self.verbose:
                logger.info(f"Validation result: {validation_response} -> {'SAFE' if is_safe else 'DANGEROUS'}")
                
            return is_safe, query
            
        except Exception as e:
            logger.warning(f"Validation failed, proceeding without validation: {e}")
            return True, query
    
    async def process_query(self, query: str) -> AgentResponse:
        """
        Process user query with hybrid architecture.
        
        Flow:
        1. Validation with Groq (if available)
        2. File operations with GPT-4o
        
        Args:
            query: User query to process
            
        Returns:
            Structured and validated AgentResponse
        """
        try:
            if self.verbose:
                logger.info(f"Processing hybrid query: {query}")
            
            # Step 1: Validation with Groq (optional)
            is_valid, sanitized_query = await self._validate_query(query)
            
            if not is_valid:
                return AgentResponse(
                    success=False,
                    message="Query is invalid or potentially dangerous",
                    type="validation_error",
                    reasoning="Query blocked by validation system for security reasons"
                )
            
            # Step 2: File operations with GPT-4o
            if self.verbose:
                logger.info(f"Executing file operations with GPT-4o")
                
            result = await self.file_operations_agent.run(sanitized_query, deps=self.dependencies)
            response = result.data
            
            if self.verbose:
                logger.info(f"Hybrid query processed successfully. Result type: {response.type}")
                
            return response
            
        except Exception as e:
            logger.error(f"Error processing hybrid query: {e}")
            
            # Ultimate fallback - prova a dare una risposta utile anche in caso di errore
            fallback_message = f"I encountered some technical difficulties, but let me try to help you anyway. "
            
            # Analizza la query per dare suggerimenti specifici
            query_lower = query.lower()
            if "list" in query_lower or "files" in query_lower:
                fallback_message += "You asked about listing files. The directory contains files that can be accessed directly."
            elif "read" in query_lower:
                fallback_message += "You asked to read a file. Try specifying the exact filename if it exists."
            elif "write" in query_lower or "create" in query_lower:
                fallback_message += "You asked to write/create a file. I can help create files in the working directory."
            elif "delete" in query_lower:
                fallback_message += "You asked to delete a file. Please specify the exact filename for deletion."
            else:
                fallback_message += "Please try rephrasing your request with more specific file operations."
            
            fallback_message += f" Technical error: {str(e)}"
            
            return AgentResponse(
                success=False,
                message=fallback_message,
                type="error_with_fallback",
                reasoning=f"Provided fallback assistance despite error: {str(e)}"
            )
    
    def process_query_sync(self, query: str) -> AgentResponse:
        """
        Synchronous version of process_query for compatibility.
        
        Args:
            query: User query to process
            
        Returns:
            Structured and validated AgentResponse
        """
        import asyncio
        try:
            # Create event loop if none exists
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.process_query(query))
    
    def get_status(self) -> Dict[str, Any]:
        """
        Return hybrid agent status.
        
        Returns:
            Dict with status information
        """
        return {
            "agent_type": "PydanticFileAgent (Hybrid)",
            "framework": "Pydantic-AI Hybrid",
            "architecture": "OpenAI GPT-4o + Groq llama-3.1-8b-instant",
            "base_directory": self.base_directory,
            "file_operations_model": str(self.file_operations_agent.model),
            "validation_model": "llama-3.1-8b-instant" if self.validation_agent else "None",
            "validation_enabled": bool(self.validation_agent),
            "tools_available": [
                "list_files_tool", 
                "read_file_tool", 
                "write_file_tool", 
                "delete_file_tool", 
                "answer_question_tool"
            ],
            "structured_output": True,
            "validation": True,
            "security_layer": bool(self.validation_agent)
        }
    
    def get_help(self) -> str:
        """
        Return help information about the hybrid agent.
        
        Returns:
            Help string
        """
        validation_status = "✅ Enabled" if self.validation_agent else "❌ Disabled"
        
        return f"""PydanticFileAgent (Hybrid) - File operations agent with hybrid architecture

ARCHITECTURE:
• OpenAI GPT-4o: File operations and advanced reasoning
• Groq llama-3.1-8b-instant: Query validation and security ({validation_status})

🔧 SUPPORTED OPERATIONS:
• List files with detailed metadata
• Read file contents  
• Write and create files
• Delete files
• Intelligent file analysis and content search

FEATURES:
• Structured output validated with Pydantic
• Automatic multi-step reasoning with GPT-4o
• Security validation with Groq (if enabled)
• Declarative tool orchestration
• Type-safe dependency injection
• Robust error handling with fallback

SECURITY:
• Automatic query validation (if Groq is configured)
• Sanitization of potentially dangerous commands
• Prevention of path traversal and unauthorized access

USAGE:
Use natural language queries to interact with the agent.
Examples: "list all files", "read config.json", "create a file test.txt".""" 