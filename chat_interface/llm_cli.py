#!/usr/bin/env python3
"""
Enhanced CLI interface for LLM-powered File Operations Agent.
Supports GPT-4o for main reasoning and LLaMA 3 8B for prompt validation.
"""
import asyncio
import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Any
import logging

# Aggiungi il path del progetto
sys.path.append(str(Path(__file__).parent.parent))

from agent import LLMFileAgent


class LLMFileAgentCLI:
    """
    Interfaccia CLI per l'agente LLM-powered.
    Supporta integrazione con OpenAI GPT-4o e Groq LLaMA 3 8B.
    """
    
    def __init__(self, base_directory: str, verbose: bool = False):
        """
        Inizializza la CLI.
        
        Args:
            base_directory: Directory base per le operazioni sui file
            verbose: Flag per output dettagliato
        """
        self.base_directory = Path(base_directory).resolve()
        self.verbose = verbose
        self.agent = None
        self.session_active = True
        
        # Configura logging
        if verbose:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.WARNING)
    
    def initialize_agent(self, openai_api_key: str = None, groq_api_key: str = None) -> bool:
        """
        Inizializza l'agente LLM con le API keys.
        
        Args:
            openai_api_key: OpenAI API key
            groq_api_key: Groq API key (opzionale)
            
        Returns:
            True se l'inizializzazione è riuscita
        """
        try:
            self.agent = LLMFileAgent(
                base_directory=str(self.base_directory),
                openai_api_key=openai_api_key,
                groq_api_key=groq_api_key,
                verbose=self.verbose
            )
            return True
        except Exception as e:
            print(f"❌ Failed to initialize LLM agent: {e}")
            return False
    
    def print_welcome(self):
        """Stampa il messaggio di benvenuto."""
        print("🤖 LLM File Operations Agent CLI")
        print("=" * 50)
        print(f"📁 Working directory: {self.base_directory}")
        
        if self.agent:
            agent_info = self.agent.get_agent_info()
            print(f"🧠 Main model: {agent_info['main_model']['name']} ({agent_info['main_model']['provider']})")
            
            validator_info = agent_info['validator_model']
            if validator_info['available']:
                print(f"🛡️  Validator: {validator_info['model']} ({validator_info['provider']})")
            else:
                print("🛡️  Validator: Pattern-based fallback (no API key)")
        
        print("\nType your requests in natural language!")
        print("Examples:")
        print("• 'Show me all files in the directory'")
        print("• 'Read the content of example.txt'") 
        print("• 'What is the largest file?'")
        print("• 'Create a file called notes.txt with some content'")
        print("\nSpecial commands: /help, /info, /clear, /quit")
        print("-" * 50)
    
    def print_help(self):
        """Stampa l'help dell'agente."""
        if self.agent:
            print(self.agent.get_help())
        else:
            print("❌ Agent not initialized. Cannot provide help.")
    
    def print_agent_info(self):
        """Stampa informazioni dettagliate sull'agente."""
        if not self.agent:
            print("❌ Agent not initialized.")
            return
        
        info = self.agent.get_agent_info()
        print("\n📊 Agent Information:")
        print(f"Type: {info['agent_type']}")
        print(f"Directory: {info['base_directory']}")
        print(f"Conversation length: {info['conversation_length']} exchanges")
        
        print(f"\n🧠 Main Model:")
        main_model = info['main_model']
        print(f"  • {main_model['name']} ({main_model['provider']})")
        print(f"  • Purpose: {main_model['purpose']}")
        
        print(f"\n🛡️  Validator Model:")
        validator = info['validator_model']
        print(f"  • {validator['model']} ({validator['provider']})")
        print(f"  • Purpose: {validator['purpose']}")
        print(f"  • Available: {validator['available']}")
        
        print(f"\n🔧 Available Tools: {len(info['available_tools'])}")
        for tool in info['available_tools']:
            print(f"  • {tool}")
        
        print(f"\n✨ Capabilities:")
        for capability in info['capabilities']:
            print(f"  • {capability}")
    
    def handle_special_command(self, command: str) -> bool:
        """
        Gestisce i comandi speciali.
        
        Args:
            command: Comando da gestire
            
        Returns:
            True se è stato gestito un comando speciale
        """
        command = command.lower().strip()
        
        if command == "/help":
            self.print_help()
            return True
        elif command == "/info":
            self.print_agent_info()
            return True
        elif command == "/clear":
            if self.agent:
                self.agent.clear_conversation_history()
                print("🧹 Conversation history cleared.")
            else:
                print("❌ Agent not initialized.")
            return True
        elif command == "/quit" or command == "/exit":
            print("👋 Goodbye!")
            self.session_active = False
            return True
        
        return False
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Processa una query utente.
        
        Args:
            query: Query dell'utente
            
        Returns:
            Risultato dell'elaborazione
        """
        if not self.agent:
            return {
                "success": False,
                "message": "Agent not initialized. Please restart with valid API keys.",
                "reasoning": "Agent initialization failed"
            }
        
        try:
            print("🤔 Thinking...")
            result = await self.agent.process_query(query)
            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing query: {str(e)}",
                "reasoning": f"Processing error: {str(e)}"
            }
    
    def format_response(self, result: Dict[str, Any]):
        """
        Formatta e stampa la risposta dell'agente.
        
        Args:
            result: Risultato dell'elaborazione
        """
        if result["success"]:
            print(f"🤖 {result['message']}")
            
            if self.verbose:
                print(f"\n🔍 Validation: {result.get('validation_result', 'unknown')}")
                print(f"📝 Reasoning: {result.get('reasoning', 'none')}")
        else:
            print(f"❌ {result['message']}")
            
            if self.verbose and 'reasoning' in result:
                print(f"📝 Reason: {result['reasoning']}")
    
    async def run_interactive_session(self):
        """Avvia la sessione interattiva."""
        self.print_welcome()
        
        if not self.agent:
            print("❌ Cannot start session: Agent not initialized")
            return
        
        print("\n💬 Ready for your questions!")
        
        while self.session_active:
            try:
                # Input utente
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Gestisci comandi speciali
                if user_input.startswith('/'):
                    self.handle_special_command(user_input)
                    continue
                
                # Processa la query normale
                result = await self.process_query(user_input)
                self.format_response(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Session ended. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()


def setup_api_keys() -> tuple[str, str]:
    """
    Configura le API keys, chiedendole all'utente se necessario.
    
    Returns:
        Tuple (openai_key, groq_key)
    """
    # Controlla variabili d'ambiente
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    # Chiedi OpenAI key se mancante (obbligatoria)
    if not openai_key:
        print("🔑 OpenAI API key required for GPT-4o")
        openai_key = input("Enter your OpenAI API key: ").strip()
        
        if not openai_key:
            print("❌ OpenAI API key is required. Exiting.")
            sys.exit(1)
    
    # Chiedi Groq key se mancante (opzionale)
    if not groq_key:
        print("\n🔑 Groq API key is optional for enhanced validation")
        print("Without it, basic pattern-based validation will be used.")
        groq_key = input("Enter your Groq API key (or press Enter to skip): ").strip()
        
        if not groq_key:
            print("⚠️  Continuing without Groq API key (pattern-based validation)")
            groq_key = None
    
    return openai_key, groq_key


async def main():
    """Funzione principale."""
    parser = argparse.ArgumentParser(
        description="LLM File Operations Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python llm_cli.py --directory ./test_files --verbose
  python llm_cli.py --directory ~/Documents --openai-key YOUR_KEY
  
Environment Variables:
  OPENAI_API_KEY    - OpenAI API key for GPT-4o
  GROQ_API_KEY      - Groq API key for LLaMA 3 8B validation (optional)
        """
    )
    
    parser.add_argument(
        '--directory',
        type=str,
        default='./test_files',
        help='Base directory for file operations (default: ./test_files)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
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
    
    # Setup directory
    directory = Path(args.directory).resolve()
    if not directory.exists():
        print(f"📁 Creating directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    
    # Setup API keys
    openai_key = args.openai_key or os.getenv("OPENAI_API_KEY")
    groq_key = args.groq_key or os.getenv("GROQ_API_KEY")
    
    if not openai_key or not groq_key:
        openai_key, groq_key = setup_api_keys()
    
    # Inizializza CLI
    cli = LLMFileAgentCLI(str(directory), verbose=args.verbose)
    
    # Inizializza agente
    if not cli.initialize_agent(openai_key, groq_key):
        print("❌ Failed to initialize agent. Exiting.")
        sys.exit(1)
    
    # Avvia sessione interattiva
    await cli.run_interactive_session()


if __name__ == "__main__":
    asyncio.run(main()) 