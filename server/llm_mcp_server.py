"""
What the server does:
- Starts a Custom ReAct agent with GPT-4o for advanced reasoning
- Exposes the agent via MCP protocol to external clients (Claude Desktop in my case)
- Handles JSON-RPC communication stdin/stdout with clients
"""
import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import os
import signal

# Configurazione logging - log su stderr, non stdout, poichè il server è in ascolto su stdin/stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Log su stderr, non stdout!
        logging.FileHandler('/tmp/llm_mcp_server.log', mode='a')  # Log file per debug
    ]
)
logger = logging.getLogger(__name__)

# Aggiungi il path del progetto per importare i moduli
sys.path.append(str(Path(__file__).parent.parent))

try:
    from agent import LLMFileAgent
    logger.info("LLMFileAgent imported successfully")
except ImportError as e:
    logger.error(f"Failed to import LLMFileAgent: {e}")
    logger.error(f"Python path: {sys.path}")
    sys.exit(1)


class LLMMCPServer:
    """
    Enhanced MCP Server che usa Custom ReAct Agent con GPT-4o.
    Implementa il protocollo Model Context Protocol con reasoning LLM avanzato.
    """
    
    def __init__(self, base_directory: str, openai_api_key: str = None, groq_api_key: str = None, server_name: str = "llm-file-operations-agent"):
        """
        Inizializza il server MCP con Custom ReAct agent.
        
        Args:
            base_directory: Directory base per le operazioni sui file
            openai_api_key: OpenAI API key per GPT-4o
            groq_api_key: Groq API key per LLaMA 3 8B validation
            server_name: Nome del server MCP
        """
        self.base_directory = Path(base_directory).resolve()
        self.server_name = server_name
        self.agent = None
        self.capabilities = {
            "resources": {},
            "tools": {},
            "prompts": {}
        }
        
        # Inizializza l'agente LLM
        self._initialize_agent(openai_api_key, groq_api_key)
        
        # Registra tool e capabilities
        self._register_capabilities()
    
    def _initialize_agent(self, openai_api_key: str = None, groq_api_key: str = None):
        """Inizializza l'agente Custom ReAct FileOperations."""
        try:
            self.agent = LLMFileAgent(
                base_directory=str(self.base_directory),
                openai_api_key=openai_api_key,
                groq_api_key=groq_api_key,
                verbose=False  # Verbose=False per il server
            )
            logger.info(f"Custom ReAct Agent initialized for directory: {self.base_directory}")
            
            # Log delle informazioni sull'agente
            agent_info = self.agent.get_agent_info()
            logger.info(f"Main model: {agent_info['main_model']['name']}")
            logger.info(f"Validator available: {agent_info['validator_model']['available']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Custom ReAct agent: {e}")
            raise
    
    def _register_capabilities(self):
        """Registra le capabilities e i tool disponibili."""
        # Tool capabilities - Enhanced with LLM reasoning
        self.capabilities["tools"] = {
            "llm_query": {
                "description": "Send a natural language query to the Custom ReAct agent for intelligent file operations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query (e.g., 'Show me all Python files and their purposes', 'Create a summary of all text files')"
                        }
                    },
                    "required": ["query"]
                }
            },
            "list_files": {
                "description": "List all files in the working directory with metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "read_file": {
                "description": "Read the complete content of a specific file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to read"
                        }
                    },
                    "required": ["filename"]
                }
            },
            "write_file": {
                "description": "Write content to a file (create or overwrite)",
                "inputSchema": {
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
            },
            "delete_file": {
                "description": "Delete a file from the working directory",
                "inputSchema": {
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
        }
        
        # Prompts capabilities
        self.capabilities["prompts"] = {
            "llm_help": {
                "description": "Get comprehensive help for the Custom ReAct file operations agent",
                "arguments": []
            },
            "agent_info": {
                "description": "Get detailed information about the Custom ReAct agent capabilities and models",
                "arguments": []
            },
            "directory_overview": {
                "description": "Get an intelligent overview of the current working directory",
                "arguments": []
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gestisce una richiesta MCP.
        
        Args:
            request: Richiesta JSON-RPC
            
        Returns:
            Risposta JSON-RPC
        """
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            logger.info(f"Handling request: {method}")
            
            # Route della richiesta al metodo appropriato
            if method == "initialize":
                response = await self._handle_initialize(params)
            elif method == "tools/list":
                response = await self._handle_tools_list()
            elif method == "tools/call":
                response = await self._handle_tool_call(params)
            elif method == "prompts/list":
                response = await self._handle_prompts_list()
            elif method == "prompts/get":
                response = await self._handle_prompt_get(params)
            elif method == "resources/list":
                response = await self._handle_resources_list()
            else:
                response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            # Aggiungi l'ID della richiesta alla risposta
            if request_id is not None:
                response["id"] = request_id
            else:
                # Se l'ID è None, impostiamo un ID di default
                response["id"] = 0
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id") if request.get("id") is not None else 0,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisce la richiesta di inizializzazione."""
        agent_info = self.agent.get_agent_info()
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": self.capabilities,
                "serverInfo": {
                    "name": self.server_name,
                    "version": "2.0.0",
                    "description": f"Custom ReAct File Operations Agent MCP Server - Working directory: {self.base_directory}",
                    "agent_type": agent_info["agent_type"],
                    "main_model": agent_info["main_model"]["name"],
                    "validator_model": agent_info["validator_model"]["model"]
                }
            }
        }
    
    async def _handle_tools_list(self) -> Dict[str, Any]:
        """Lista tutti i tool disponibili."""
        tools = []
        for name, config in self.capabilities["tools"].items():
            tools.append({
                "name": name,
                "description": config["description"],
                "inputSchema": config["inputSchema"]
            })
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Esegue una chiamata a un tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        try:
            if tool_name == "llm_query":
                result = await self._execute_llm_query(arguments)
            elif tool_name == "list_files":
                result = await self._execute_list_files()
            elif tool_name == "read_file":
                result = await self._execute_read_file(arguments)
            elif tool_name == "write_file":
                result = await self._execute_write_file(arguments)
            elif tool_name == "delete_file":
                result = await self._execute_delete_file(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def _execute_llm_query(self, arguments: Dict[str, Any]) -> str:
        """Esegue una query LLM generale (tool principale)."""
        query = arguments.get("query")
        if not query:
            return "Error: query parameter is required"
        
        try:
            result = await self.agent.process_query(query)
            if result.get("success"):
                return result.get("message", "Query processed successfully")
            else:
                return f"Query rejected: {result.get('message', 'Unknown error')}"
        except Exception as e:
            return f"Error processing LLM query: {e}"
    
    async def _execute_list_files(self) -> str:
        """Esegue list_files attraverso l'agente."""
        try:
            files_list = self.agent.tool_registry.execute_tool("list_files")
            if not files_list:
                return "No files found in the directory."
            
            result = "Files in the directory:\n\n"
            for file_info in files_list:
                result += f"📄 {file_info['name']} ({file_info['size']} bytes)\n"
            
            return result
        except Exception as e:
            return f"Error listing files: {e}"
    
    async def _execute_read_file(self, arguments: Dict[str, Any]) -> str:
        """Esegue read_file attraverso l'agente."""
        filename = arguments.get("filename")
        if not filename:
            return "Error: filename parameter is required"
        
        try:
            content = self.agent.tool_registry.execute_tool("read_file", filename=filename)
            return f"Content of {filename}:\n\n{content}"
        except Exception as e:
            return f"Error reading file {filename}: {e}"
    
    async def _execute_write_file(self, arguments: Dict[str, Any]) -> str:
        """Esegue write_file attraverso l'agente."""
        filename = arguments.get("filename")
        content = arguments.get("content")
        mode = arguments.get("mode", "w")
        
        if not filename or content is None:
            return "Error: filename and content parameters are required"
        
        try:
            result = self.agent.tool_registry.execute_tool(
                "write_file", 
                filename=filename, 
                content=content, 
                mode=mode
            )
            if result:
                return f"Successfully wrote content to {filename}"
            else:
                return f"Failed to write to {filename}"
        except Exception as e:
            return f"Error writing file {filename}: {e}"
    
    async def _execute_delete_file(self, arguments: Dict[str, Any]) -> str:
        """Esegue delete_file attraverso l'agente."""
        filename = arguments.get("filename")
        if not filename:
            return "Error: filename parameter is required"
        
        try:
            result = self.agent.tool_registry.execute_tool("delete_file", filename=filename)
            if result:
                return f"Successfully deleted {filename}"
            else:
                return f"Failed to delete {filename}"
        except Exception as e:
            return f"Error deleting file {filename}: {e}"
    
    async def _handle_prompts_list(self) -> Dict[str, Any]:
        """Lista tutti i prompt disponibili."""
        prompts = []
        for name, config in self.capabilities["prompts"].items():
            prompts.append({
                "name": name,
                "description": config["description"],
                "arguments": config["arguments"]
            })
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "prompts": prompts
            }
        }
    
    async def _handle_prompt_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ottiene il contenuto di un prompt specifico."""
        prompt_name = params.get("name")
        
        if prompt_name == "llm_help":
            content = self.agent.get_help()
        elif prompt_name == "agent_info":
            agent_info = self.agent.get_agent_info()
            content = f"""Custom ReAct File Operations Agent Information:

Type: {agent_info['agent_type']}
Directory: {agent_info['base_directory']}

Main Model: {agent_info['main_model']['name']} ({agent_info['main_model']['provider']})
Purpose: {agent_info['main_model']['purpose']}

Validator: {agent_info['validator_model']['model']} ({agent_info['validator_model']['provider']})
Available: {agent_info['validator_model']['available']}

Conversation Length: {agent_info['conversation_length']} exchanges
Available Tools: {len(agent_info['available_tools'])}

Capabilities:
{chr(10).join('• ' + cap for cap in agent_info['capabilities'])}"""
        elif prompt_name == "directory_overview":
            try:
                # Usa l'LLM per generare una overview intelligente
                overview_result = await self.agent.process_query("Give me an intelligent overview of all files in this directory, including their purposes and relationships")
                if overview_result.get("success"):
                    content = overview_result.get("message", "No overview available")
                else:
                    # Fallback a overview semplice
                    files_list = self.agent.tool_registry.execute_tool("list_files")
                    content = f"Working Directory: {self.base_directory}\n\n"
                    content += f"Total files: {len(files_list) if files_list else 0}\n\n"
                    if files_list:
                        content += "Files:\n"
                        for file_info in files_list:
                            content += f"- {file_info['name']} ({file_info['size']} bytes)\n"
                    else:
                        content += "Directory is empty."
            except Exception as e:
                content = f"Error getting directory overview: {e}"
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": f"Unknown prompt: {prompt_name}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "description": f"Generated content for {prompt_name}",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": content
                        }
                    }
                ]
            }
        }
    
    async def _handle_resources_list(self) -> Dict[str, Any]:
        """Lista tutte le risorse disponibili."""
        return {
            "jsonrpc": "2.0",
            "result": {
                "resources": []
            }
        }


async def run_server(base_directory: str, openai_api_key: str = None, groq_api_key: str = None, server_name: str = "llm-file-operations-agent"):
    """
    Avvia il server LLM MCP con gestione errori robusta.
    
    Args:
        base_directory: Directory base per le operazioni sui file
        openai_api_key: OpenAI API key
        groq_api_key: Groq API key
        server_name: Nome del server MCP
    """
    logger.info(f"🚀 Starting LLM MCP server: {server_name}")
    logger.info(f"📁 Working directory: {base_directory}")
    logger.info(f"🐍 Python executable: {sys.executable}")
    logger.info(f"🔑 OpenAI key: {'✅ Set' if openai_api_key else '❌ Missing'}")
    logger.info(f"🔑 Groq key: {'✅ Set' if groq_api_key else '❌ Missing'}")
    
    # Verifica che la directory esista
    if not Path(base_directory).exists():
        logger.error(f"❌ Directory does not exist: {base_directory}")
        sys.exit(1)
    
    try:
        server = LLMMCPServer(base_directory, openai_api_key, groq_api_key, server_name)
        logger.info("✅ LLM Server instance created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create LLM server instance: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)
    
    # Setup signal handlers per shutdown graceful
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("📡 Starting stdin/stdout communication loop...")
    
    # Loop principale del server MIGLIORATO
    request_count = 0
    try:
        while True:
            try:
                request_count += 1
                logger.debug(f"📥 Waiting for request #{request_count}...")
                
                # Leggi richiesta da stdin con timeout
                line = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline),
                    timeout=300.0  # 5 minuti timeout per evitare hang infiniti
                )
                
                if not line:
                    logger.info("📪 Empty line received - client disconnected")
                    break
                
                line = line.strip()
                if not line:
                    logger.debug("📝 Empty line skipped")
                    continue
                
                logger.debug(f"📨 Received: {line[:100]}...")  # Log primi 100 char
                
                try:
                    request = json.loads(line)
                    logger.debug(f"📋 Parsed request method: {request.get('method', 'unknown')}")
                    
                    response = await server.handle_request(request)
                    
                    # Scrivi risposta a stdout
                    response_json = json.dumps(response)
                    print(response_json)
                    sys.stdout.flush()
                    
                    logger.debug(f"📤 Response sent for request #{request_count}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON in request #{request_count}: {e}")
                    logger.error(f"   Line content: {line}")
                    # Invia errore di parsing
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
                except Exception as e:
                    logger.error(f"❌ Error processing request #{request_count}: {e}")
                    logger.exception("Full traceback:")
                    # Invia errore interno
                    error_response = {
                        "jsonrpc": "2.0", 
                        "id": request.get("id") if 'request' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
            
            except asyncio.TimeoutError:
                logger.warning("⏰ Timeout waiting for input - continuing...")
                # Continua invece di terminare
                continue
                
            except Exception as e:
                logger.error(f"❌ Critical error in main loop: {e}")
                logger.exception("Full traceback:")
                break
    
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal server error: {e}")
        logger.exception("Full traceback:")
    finally:
        logger.info("🔚 LLM MCP Server shutting down...")
        logger.info(f"📊 Total requests processed: {request_count}")


def main():
    """Funzione principale per avviare il server LLM MCP."""
    # Configurazione logging aggiuntiva per main
    logger.info("🎬 LLM MCP Server starting up...")
    
    parser = argparse.ArgumentParser(
        description="Custom ReAct File Operations Agent MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--directory',
        type=str,
        default='./test_files',
        help='Base directory for file operations (default: ./test_files)'
    )
    
    parser.add_argument(
        '--name',
        type=str,
        default='llm-file-operations-agent',
        help='Server name (default: llm-file-operations-agent)'
    )
    
    parser.add_argument(
        '--openai-key',
        type=str,
        help='OpenAI API key (overrides OPENAI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--groq-key',
        type=str,
        help='Groq API key (overrides GROQ_API_KEY env var)'
    )
    
    args = parser.parse_args()
    
    # Risolvi il percorso assoluto
    base_directory = str(Path(args.directory).resolve())
    
    # Setup API keys
    openai_key = args.openai_key or os.getenv("OPENAI_API_KEY")
    groq_key = args.groq_key or os.getenv("GROQ_API_KEY")
    
    logger.info(f"🔧 Configuration: directory={base_directory}, name={args.name}")
    logger.info(f"🔑 API Keys: OpenAI={'✅ Set' if openai_key else '❌ Missing'}, Groq={'✅ Set' if groq_key else '❌ Missing'}")
    
    if not openai_key:
        logger.error("❌ OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --openai-key")
        sys.exit(1)
    
    # Avvia il server
    try:
        asyncio.run(run_server(base_directory, openai_key, groq_key, args.name))
    except Exception as e:
        logger.error(f"❌ Failed to start LLM server: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main() 