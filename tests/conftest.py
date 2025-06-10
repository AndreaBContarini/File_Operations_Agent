"""
Pytest configuration and shared fixtures for the test suite.
It is used to create a temporary directory for testing file operations.
Configuration of LLM agents with API keys
Essential for the proper functioning of pytest, because it allows to test the agent with real API keys.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import os


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for testing file operations."""
    temp_dir = tempfile.mkdtemp()
    
    # Create some test files
    test_files = {
        "example.txt": "Hello World",
        "script.py": "print('Hello Python')",
        "data.json": '{"name": "test", "value": 123}',
        "large_file.txt": "This is a larger file with more content for testing purposes.",
        "empty.txt": ""
    }
    
    for filename, content in test_files.items():
        file_path = Path(temp_dir) / filename
        file_path.write_text(content, encoding='utf-8')
    
    yield temp_dir
    
    # Cleanup: elimina la directory temporanea
    shutil.rmtree(temp_dir)


@pytest.fixture
def agent(temp_test_dir):
    """Create a FileOperationsAgent instance for testing."""
    # NOTE: Deterministic agent(created at the beginning, for initial testing) removed - this fixture maintained for compatibility
    pytest.skip("Deterministic agent was removed from project architecture")


@pytest.fixture
def llm_agent(temp_test_dir):
    """Create a Custom ReAct Agent instance for testing (if API keys available)."""
    try:
        from agent.llm_agent import LLMFileAgent
        
        # Only create if API keys are available
        openai_key = os.getenv("OPENAI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        
        if openai_key:
            return LLMFileAgent(temp_test_dir, openai_api_key=openai_key, groq_api_key=groq_key)
        else:
            pytest.skip("OpenAI API key not available")
    except Exception as e:
        pytest.skip(f"Custom ReAct Agent not available: {e}")


@pytest.fixture
def sample_files_content():
    """Sample file contents for testing."""
    return {
        "test1.txt": "First test file content",
        "test2.py": "# Python script\nprint('test')",
        "config.json": '{"setting": "value", "number": 42}',
        "readme.md": "# Test Project\n\nThis is a test.",
        "log.txt": "2024-01-01 INFO: Test log entry"
    } 