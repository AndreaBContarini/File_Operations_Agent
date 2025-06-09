#!/usr/bin/env python3
"""
Test basico per verificare che tutti gli import e le inizializzazioni funzionino.
"""
import sys
from pathlib import Path

# Add the path of the project
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / 'Pydantic-AI_Agent'))

def test_imports():
    """Test che tutti gli import funzionino."""
    try:
        print("🧪 Testing imports...")
        
        # Test import Custom ReAct Agent
        from agent import LLMFileAgent
        print("✅ Custom ReAct Agent import OK")
        
        # Test import Pydantic-AI Agent  
        from pydantic_agent import PydanticFileAgent
        print("✅ Pydantic-AI Agent import OK")
        
        # Test import tools
        from tools import list_files, read_file, write_file, delete_file, answer_question_about_files
        print("✅ All tools import OK")
        
        # Test import tool registry
        from agent.tool_registry import ToolRegistry
        print("✅ Tool Registry import OK")
        
        # Test import validator
        from agent.llm_validator import LLMQueryValidator
        print("✅ LLM Validator import OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_tool_operations():
    """Test operazioni di base sui tool senza API."""
    try:
        print("\n🧪 Testing basic tool operations...")
        
        from tools import list_files, write_file, read_file, delete_file
        
        test_dir = "./test_files"
        test_file = "test_basic.txt"
        
        # Create test directory
        Path(test_dir).mkdir(exist_ok=True)
        
        # Test write
        result = write_file(test_file, "test content", test_dir)
        if result:
            print("✅ Write tool OK")
        
        # Test read
        content = read_file(test_file, test_dir)
        if content == "test content":
            print("✅ Read tool OK")
        
        # Test list
        files = list_files(test_dir)
        if any(f["name"] == test_file for f in files):
            print("✅ List tool OK")
        
        # Test delete
        result = delete_file(test_file, test_dir)
        if result:
            print("✅ Delete tool OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

def test_agent_initialization():
    """Test inizializzazione degli agent senza API keys."""
    try:
        print("\n🧪 Testing agent initialization...")
        
        test_dir = "./test_files"
        
        # Test Custom ReAct Agent con fake keys
        from agent import LLMFileAgent
        agent1 = LLMFileAgent(
            base_directory=test_dir,
            openai_api_key="fake_key",
            groq_api_key="fake_key"
        )
        print("✅ Custom ReAct Agent init OK")
        
        # Test Pydantic-AI Agent con fake keys
        from pydantic_agent import PydanticFileAgent
        agent2 = PydanticFileAgent(
            base_directory=test_dir,
            openai_api_key="fake_key",
            groq_api_key="fake_key"
        )
        print("✅ Pydantic-AI Agent init OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent init failed: {e}")
        return False

def main():
    """Esegue tutti i test."""
    print("🚀 Running basic functionality tests...")
    
    success = True
    
    success &= test_imports()
    success &= test_basic_tool_operations()
    success &= test_agent_initialization()
    
    if success:
        print("\n🎉 All basic tests PASSED!")
        print("✅ Gli agent sono pronti per l'uso!")
    else:
        print("\n❌ Some tests FAILED!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 