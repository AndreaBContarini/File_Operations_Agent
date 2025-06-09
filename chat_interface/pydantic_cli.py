#!/usr/bin/env python3
"""
CLI Interface interattiva per l'agente Pydantic-AI.
Fornisce un'interfaccia terminale user-friendly identica all'originale.
"""
import os
import sys
import argparse
import asyncio
import getpass
from typing import Optional, Dict, Any
from pathlib import Path

# Add the path of the project for importing modules
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / 'Pydantic-AI_Agent'))

from pydantic_agent import PydanticFileAgent


def get_api_credentials():
    """
    Get API credentials interactively from user.
    
    Returns: tuple: (openai_api_key, groq_api_key_optional)
    """
    print("\n🤖 API Configuration for Pydantic-AI Hybrid Agent")
    print("=" * 60)
    
    print("\n🎯 HYBRID ARCHITECTURE:")
    print("  • GPT-4o: File operations (REQUIRED)")
    print("  • Groq llama-3.1-8b-instant: Query validation (OPTIONAL)")
    
    # OpenAI API Key (REQUIRED)
    print(f"\n🔑 Enter your OpenAI API key (REQUIRED):")
    print("   (Used for GPT-4o file operations)")
    openai_api_key = getpass.getpass("🔐 OpenAI API Key: ").strip()
    
    if not openai_api_key or not (openai_api_key.startswith('sk-') or openai_api_key.startswith('sk-proj-')):
        print("❌ Invalid OpenAI API key!")
        return None
    
    # Groq API Key (OPTIONAL)
    print(f"\n🔑 Enter your Groq API key (OPTIONAL):")
    print("   (Used for llama-3.1-8b-instant validation)")
    print("   (Press ENTER to skip)")
    groq_api_key = getpass.getpass("🔐 Groq API Key (optional): ").strip()
    
    if groq_api_key and not groq_api_key.startswith('gsk_'):
        print("❌ Invalid Groq API key! Continuing without validation...")
        groq_api_key = None
    
    print(f"\n✅ Configuration completed!")
    print(f"   OpenAI GPT-4o: ✅ Configured for file operations")
    if groq_api_key:
        print(f"   Groq llama-3.1-8b-instant: ✅ Configured for query validation")
    else:
        print(f"   Groq: ❌ Not configured (validation skipped)")
    
    return openai_api_key, groq_api_key


class PydanticFileAgentCLI:
    """
    CLI Interface for the hybrid PydanticFileAgent.
    Handles special commands and interactive conversation.
    """
    
    def __init__(self, base_directory: str, openai_api_key: str, groq_api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize CLI with hybrid Pydantic-AI agent.
        
        Args:
            base_directory: Base directory for file operations
            openai_api_key: API key for OpenAI (required)
            groq_api_key: API key for Groq (optional)
            verbose: Whether to enable verbose agent output
        """
        self.base_directory = base_directory
        self.openai_api_key = openai_api_key
        self.groq_api_key = groq_api_key
        self.verbose = verbose
        self.agent = None
        self.is_running = True
        
        # Special commands supported
        self.special_commands = {
            '/help': self._show_help,
            '/quit': self._quit,
            '/exit': self._quit,
            '/status': self._show_status,
            '/clear': self._clear_screen,
            '/verbose': self._toggle_verbose,
            '/directory': self._show_directory,
            '/commands': self._show_commands
        }
        
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize hybrid Pydantic-AI agent with error handling."""
        try:
            self.agent = PydanticFileAgent(
                base_directory=self.base_directory,
                openai_api_key=self.openai_api_key,
                groq_api_key=self.groq_api_key,
                verbose=self.verbose
            )
            
            print(f"✅ Pydantic-AI Hybrid Agent initialized successfully!")
            print(f"📁 Working directory: {self.base_directory}")
            print(f"🤖 Operations Provider: OpenAI GPT-4o")
            if self.groq_api_key:
                print(f"🔍 Validation Provider: Groq llama-3.1-8b-instant")
            else:
                print(f"🔍 Validation Provider: None (direct processing)")
            print(f"✨ Framework: Pydantic-AI with hybrid architecture")
            if self.verbose:
                print("🔍 Verbose mode enabled")
        except Exception as e:
            print(f"❌ Error initializing Pydantic-AI hybrid agent: {e}")
            sys.exit(1)
    
    def run(self):
        """Avvia il loop principale della CLI."""
        self._show_welcome()
        
        print("\n💬 Ready for your questions!")
        
        while self.is_running:
            try:
                # Ottieni input utente
                user_input = self._get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Gestisci comandi speciali
                if user_input.startswith('/'):
                    self._handle_special_command(user_input.strip())
                else:
                    # Elabora query normale attraverso l'agente Pydantic-AI
                    asyncio.run(self._process_query(user_input.strip()))
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using the Pydantic-AI File Operations Agent.")
                break
            except EOFError:
                print("\n\n👋 Goodbye! Thanks for using the Pydantic-AI File Operations Agent.")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("Type '/help' for assistance or '/quit' to exit.")
    
    def _get_user_input(self) -> str:
        """Ottiene input dall'utente con prompt personalizzato."""
        try:
            return input("\n👤 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            raise
    
    async def _process_query(self, query: str):
        """
        Elabora una query normale attraverso l'agente Pydantic-AI.
        
        Args:
            query: Query dell'utente da elaborare
        """
        print("🤔 Thinking...")
        
        try:
            # Elabora la query attraverso l'agente Pydantic-AI
            result = await self.agent.process_query(query)
            
            # Mostra il risultato formattato
            self._display_result(result)
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    def _display_result(self, result):
        """
        Display Pydantic-AI agent result with structured content.
        
        Args:
            result: AgentResponse from agent processing
        """
        if result.success:
            print(f"🤖 {result.message}")
            
            # Show file content if available (for read operations)
            if hasattr(result, 'file_content') and result.file_content:
                print(f"\n📄 File Content:\n{result.file_content}")
            
            # Show file list if available (for list operations)
            if hasattr(result, 'files') and result.files:
                print(f"\n📋 Files Found: {len(result.files)} items")
                if self.verbose:
                    for file_info in result.files[:5]:  # Show first 5 files
                        print(f"  • {file_info.get('name', 'unknown')} ({file_info.get('size', 0)} bytes)")
                    if len(result.files) > 5:
                        print(f"  ... and {len(result.files) - 5} more files")
            
            # Show analysis result if available
            if hasattr(result, 'analysis_result') and result.analysis_result:
                print(f"\n🔍 Analysis Result:\n{result.analysis_result}")
            
            if self.verbose:
                print(f"\n🔍 Operation Type: {result.type}")
                if result.reasoning:
                    print(f"📝 Reasoning: {result.reasoning}")
                if hasattr(result, 'operations_performed') and result.operations_performed:
                    print(f"⚡ Operations: {', '.join(result.operations_performed)}")
        else:
            print(f"❌ {result.message}")
            
            if self.verbose and result.reasoning:
                print(f"📝 Reason: {result.reasoning}")
    
    def _handle_special_command(self, command: str):
        """
        Gestisce comandi speciali della CLI.
        
        Args:
            command: Comando speciale da eseguire
        """
        # Estrae il comando base (senza parametri)
        base_command = command.split()[0]
        
        if base_command in self.special_commands:
            self.special_commands[base_command](command)
        else:
            print(f"❌ Unknown command: {command}")
            print("Type '/commands' to see all available commands.")
    
    def _show_welcome(self):
        """Show welcome message."""
        print("🤖 Pydantic-AI File Operations Agent CLI")
        print("=" * 50)
        print(f"📁 Working directory: {self.base_directory}")
        print(f"🧠 Main model: GPT-4o (OpenAI)")
        
        if self.groq_api_key:
            print(f"🛡️  Validator: llama-3.1-8b-instant (Groq)")
        else:
            print("🛡️  Validator: Direct processing (no validation)")
        
        print("\nType your requests in natural language!")
        print("Examples:")
        print("• 'Show me all files in the directory'")
        print("• 'Read the content of example.txt'") 
        print("• 'What is the largest file?'")
        print("• 'Create a file called notes.txt with some content'")
        print("\nSpecial commands: /help, /commands, /status, /quit")
        print("-" * 50)
    
    def _show_help(self, command: str):
        """Show agent help message."""
        print("\n📖 PYDANTIC-AI AGENT HELP:")
        print(self.agent.get_help())
        print("\n💡 EXAMPLE QUERIES:")
        print("• 'List all files in the directory'")
        print("• 'Read the content of config.json'") 
        print("• 'Create a file called test.txt with content Hello World'")
        print("• 'Delete the file old.txt'")
        print("• 'What is the largest file in the directory?'")
        print("• 'Analyze all Python files and tell me what they do'")
        print("• 'Create a report of JSON files found'")
    
    def _show_commands(self, command: str):
        """Show all available special commands."""
        print("\n⚡ SPECIAL COMMANDS:")
        print("  /help      - Show agent help and example queries")
        print("  /commands  - Show this command list")
        print("  /status    - Show agent status and statistics")
        print("  /directory - Show current working directory")
        print("  /verbose   - Toggle verbose mode on/off")
        print("  /clear     - Clear the screen")
        print("  /quit      - Exit the CLI")
        print("  /exit      - Exit the CLI")
    
    def _show_status(self, command: str):
        """Show current agent status."""
        try:
            status = self.agent.get_status()
            print("\n📊 PYDANTIC-AI AGENT STATUS:")
            print(f"  📁 Base Directory: {status['base_directory']}")
            print(f"  🤖 Agent Type: {status['agent_type']}")
            print(f"  🧠 Framework: {status['framework']}")
            print(f"  🏗️  Architecture: {status['architecture']}")
            print(f"  🛠️  Tools Available: {len(status['tools_available'])}")
            if self.verbose:
                print(f"  📋 Tools: {', '.join(status['tools_available'])}")
            print(f"  ✅ Structured Output: {status['structured_output']}")
            print(f"  🔍 Validation: {status['validation_enabled']}")
            print(f"  🔍 Verbose Mode: {self.verbose}")
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def _show_directory(self, command: str):
        """Show current directory information."""
        try:
            dir_path = Path(self.base_directory)
            if dir_path.exists():
                files = list(dir_path.iterdir())
                print(f"\n📁 CURRENT DIRECTORY: {self.base_directory}")
                print(f"📊 Total items: {len(files)}")
                
                if files:
                    print("\n📋 Contents:")
                    for item in sorted(files)[:10]:  # Show only first 10
                        if item.is_file():
                            size = item.stat().st_size
                            print(f"  📄 {item.name} ({size} bytes)")
                        else:
                            print(f"  📁 {item.name}/")
                    
                    if len(files) > 10:
                        print(f"  ... and {len(files) - 10} more items")
                else:
                    print("📭 Directory is empty")
            else:
                print(f"❌ Directory does not exist: {self.base_directory}")
        except Exception as e:
            print(f"❌ Error reading directory: {e}")
    
    def _toggle_verbose(self, command: str):
        """Toggle verbose mode on/off."""
        self.verbose = not self.verbose
        self.agent.verbose = self.verbose
        status = "enabled" if self.verbose else "disabled"
        print(f"🔍 Verbose mode {status}")
    
    def _clear_screen(self, command: str):
        """Clear the screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def _quit(self, command: str):
        """Exit the CLI."""
        print("👋 Goodbye! Thanks for using the Pydantic-AI File Operations Agent.")
        self.is_running = False


def create_sample_files(directory: str):
    """
    Create sample files in specified directory to test the agent.
    
    Args:
        directory: Directory where to create sample files
    """
    dir_path = Path(directory)
    dir_path.mkdir(exist_ok=True)
    
    # Simple text file
    (dir_path / "README.md").write_text("""# Test Directory

This is a test directory for the Pydantic-AI agent.
Contains various file types to test functionality.
""")
    
    # JSON file
    (dir_path / "config.json").write_text("""{
    "app_name": "Pydantic-AI Agent",
    "version": "1.0.0",
    "settings": {
        "verbose": true,
        "max_files": 100
    }
}""")
    
    # CSV file
    (dir_path / "data.csv").write_text("""name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,London
Diana,28,Paris
""")
    
    # Python file
    (dir_path / "script.py").write_text("""#!/usr/bin/env python3
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("Pydantic-AI"))
""")
    
    print(f"✅ Sample files created in {directory}")


def main():
    """Main function that handles arguments and starts CLI."""
    parser = argparse.ArgumentParser(
        description="Interactive CLI for Pydantic-AI Hybrid File Operations Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pydantic_cli.py                                    # Interactive hybrid setup
  python pydantic_cli.py -d ./test_files                   # Specify custom directory
  python pydantic_cli.py -d ./data -v                      # Enable verbose mode
  python pydantic_cli.py --create-samples                  # Create sample files first
        """
    )
    
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default='./test_files',
        help='Base directory for file operations (default: ./test_files)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--create-samples',
        action='store_true',
        help='Create sample files in the target directory before starting'
    )
    
    args = parser.parse_args()
    
    # Get API credentials interactively
    credentials = get_api_credentials()
    if not credentials:
        print("❌ API configuration failed!")
        sys.exit(1)
    openai_api_key, groq_api_key = credentials
    
    # Create directory if it doesn't exist
    Path(args.directory).mkdir(exist_ok=True)
    
    # Create sample files if requested
    if args.create_samples:
        create_sample_files(args.directory)
    
    # Start CLI
    try:
        cli = PydanticFileAgentCLI(
            base_directory=args.directory,
            openai_api_key=openai_api_key,
            groq_api_key=groq_api_key,
            verbose=args.verbose
        )
        cli.run()
    except Exception as e:
        print(f"❌ Error starting CLI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 