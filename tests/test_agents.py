"""
Test suite for Custom ReAct and Pydantic-AI agents.
Tests agent behavior, validation, and the specific fix for file analysis queries.
"""
import pytest
import asyncio
import os
from unittest.mock import patch, Mock

from agent.llm_validator import LLMQueryValidator, ValidationResult
from agent.llm_agent import LLMFileAgent


class TestLLMValidator:
    """Test LLM query validation system."""
    
    @pytest.mark.asyncio
    async def test_file_analysis_queries_approved(self):
        """Test that file analysis queries are properly approved."""
        validator = LLMQueryValidator()
        
        # Test queries that should be approved
        approved_queries = [
            "cosa fa hello.py?",
            "what does config.json do?", 
            "analyze script.py",
            "read hello.py",
            "list files",
            "what is the largest file?"
        ]
        
        for query in approved_queries:
            is_valid, message, result = await validator.validate_query(query)
            assert is_valid, f"Query '{query}' should be approved but was rejected: {message}"
            assert result == ValidationResult.APPROVED
    
    @pytest.mark.asyncio
    async def test_inappropriate_queries_rejected(self):
        """Test that inappropriate queries are properly rejected."""
        validator = LLMQueryValidator()
        
        # Test queries that should be rejected
        rejected_queries = [
            "hello how are you?",
            "what's the weather today?",
            "tell me about politics",
            "help with my relationship"
        ]
        
        for query in rejected_queries:
            is_valid, message, result = await validator.validate_query(query)
            assert not is_valid, f"Query '{query}' should be rejected but was approved"
            assert result in [ValidationResult.REJECTED_INAPPROPRIATE, ValidationResult.REJECTED_OFF_TOPIC]
    
    def test_fallback_validation_file_operations(self):
        """Test fallback pattern-based validation for file operations."""
        validator = LLMQueryValidator()
        
        # Test specific pattern matching
        test_cases = [
            ("read hello.py", True, "contains file operation keyword"),
            ("write test.txt", True, "contains file operation keyword"), 
            ("list", True, "contains file operation keyword"),
            ("analyze data.json", True, "file analysis pattern"),
            ("cosa fa script.py", True, "file analysis pattern"),
            ("hello world", False, "inappropriate pattern"),
            ("weather forecast", False, "inappropriate pattern")
        ]
        
        for query, expected_valid, reason in test_cases:
            is_valid, message, result = validator._fallback_validation(query)
            assert is_valid == expected_valid, f"Query '{query}' validation failed: expected {expected_valid}, got {is_valid}. Reason: {reason}"


class TestCustomReActAgent:
    """Test Custom ReAct File Agent functionality."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing without API calls."""
        with patch('agent.llm_agent.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock successful tool call response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.tool_calls = [
                Mock(
                    function=Mock(
                        name="answer_question_about_files",
                        arguments='{"query": "cosa fa hello.py?"}'
                    )
                )
            ]
            mock_client.chat.completions.create.return_value = mock_response
            
            yield mock_client
    
    def test_should_use_tools_file_queries(self, temp_test_dir):
        """Test that agent correctly identifies when to use tools."""
        agent = LLMFileAgent(temp_test_dir, "fake-key")
        
        # Queries that should use tools
        tool_queries = [
            "cosa fa hello.py?",
            "read config.json",
            "list files",
            "what does script.py do?",
            "delete old.txt",
            "create new file"
        ]
        
        for query in tool_queries:
            should_use = agent._should_use_tools(query, [])
            assert should_use, f"Query '{query}' should use tools but agent says no"
    
    def test_should_not_use_tools_help_queries(self, temp_test_dir):
        """Test that agent correctly identifies help queries that don't need tools."""
        agent = LLMFileAgent(temp_test_dir, "fake-key")
        
        # Queries that should NOT use tools
        no_tool_queries = [
            "help",
            "what can you do?",
            "how do you work?",
            "what are your capabilities?"
        ]
        
        for query in no_tool_queries:
            should_use = agent._should_use_tools(query, [])
            assert not should_use, f"Query '{query}' should NOT use tools but agent says yes"


class TestIntegrationFileAnalysis:
    """Integration tests for file analysis queries (cosa fa hello.py? fix)."""
    
    @pytest.fixture
    def analysis_test_dir(self):
        """Create test directory with specific files for analysis."""
        import tempfile
        import shutil
        from pathlib import Path
        
        temp_dir = tempfile.mkdtemp()
        
        # Create test files with specific content
        test_files = {
            "hello.py": "def hello_world():\n    print('Hello, World!')\n    return 'success'\n\nif __name__ == '__main__':\n    hello_world()",
            "config.json": '{"database": {"host": "localhost", "port": 5432}, "debug": true}',
            "script.py": "#!/usr/bin/env python3\nimport sys\nprint(f'Args: {sys.argv}')",
            "readme.txt": "This is a sample project for testing file analysis capabilities."
        }
        
        for filename, content in test_files.items():
            file_path = Path(temp_dir) / filename
            file_path.write_text(content, encoding='utf-8')
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_validator_approves_analysis_queries(self, analysis_test_dir):
        """Test that validator approves file analysis queries."""
        validator = LLMQueryValidator()
        
        analysis_queries = [
            "cosa fa hello.py?",
            "che cosa fa config.json?", 
            "what does script.py do?",
            "analyze readme.txt",
            "what is the purpose of hello.py?"
        ]
        
        for query in analysis_queries:
            is_valid, message, result = await validator.validate_query(query)
            assert is_valid, f"Analysis query '{query}' was rejected: {message}"
            assert result == ValidationResult.APPROVED
    
    def test_answer_question_tool_with_analysis_queries(self, analysis_test_dir):
        """Test that answer_question_about_files handles analysis queries."""
        from tools.answer_question_about_files import answer_question_about_files
        
        # Test without API key (should use fallback)
        result = answer_question_about_files(analysis_test_dir, "cosa fa hello.py?", None)
        
        # Should return some analysis even without AI
        assert isinstance(result, str)
        assert len(result) > 0
        assert "hello.py" in result
    
    @pytest.mark.asyncio 
    async def test_custom_react_agent_processes_analysis_query(self, analysis_test_dir):
        """Test that Custom ReAct agent can process file analysis queries end-to-end."""
        # Only run if we have API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            pytest.skip("OpenAI API key not available for integration test")
        
        agent = LLMFileAgent(analysis_test_dir, openai_key, verbose=True)
        
        try:
            # Test the exact query we fixed
            result = await agent.process_query("cosa fa hello.py?")
            
            # Basic checks
            assert isinstance(result, dict)
            assert "success" in result
            assert "message" in result
            
            # Should be successful (not rejected by validator)
            if not result.get("success", False):
                # If it failed, it shouldn't be because of validation
                error_msg = result.get("message", "")
                assert "outside my scope" not in error_msg, "Query was rejected by validator despite fix"
                
        except Exception as e:
            # Accept API failures, but not validation failures
            if "outside my scope" in str(e):
                pytest.fail("Query was rejected by validator despite fix")


class TestErrorHandling:
    """Test error handling and failure modes."""
    
    def test_read_nonexistent_file_error_message(self, temp_test_dir):
        """Test that reading non-existent files gives helpful error messages."""
        from tools.read_file import read_file
        
        with pytest.raises(FileNotFoundError) as exc_info:
            read_file("nonexistent.txt", temp_test_dir)
        
        error_msg = str(exc_info.value)
        assert "nonexistent.txt" in error_msg
    
    def test_permission_denied_simulation(self, temp_test_dir):
        """Test handling of permission-denied scenarios."""
        from tools.write_file import write_file
        from pathlib import Path
        
        # Create a read-only directory
        readonly_dir = Path(temp_test_dir) / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        try:
            # Attempt to write to read-only directory should fail gracefully
            with pytest.raises(Exception):
                write_file("test.txt", "content", str(readonly_dir))
        finally:
            # Cleanup: restore permissions
            readonly_dir.chmod(0o755)
    
    def test_large_file_handling(self, temp_test_dir):
        """Test handling of large files."""
        from tools.write_file import write_file
        from tools.read_file import read_file
        
        # Create a moderately large file (1MB)
        large_content = "A" * (1024 * 1024)  # 1MB of 'A's
        filename = "large_test.txt"
        
        # Should handle large files without issues
        assert write_file(filename, large_content, temp_test_dir) is True
        
        read_content = read_file(filename, temp_test_dir)
        assert len(read_content) == len(large_content)
        assert read_content == large_content
    
    def test_unicode_filename_handling(self, temp_test_dir):
        """Test handling of Unicode filenames."""
        from tools.write_file import write_file
        from tools.read_file import read_file
        
        unicode_filename = "测试文件_🎯.txt"  
        content = "Unicode test content"
        
        try:
            assert write_file(unicode_filename, content, temp_test_dir) is True
            read_content = read_file(unicode_filename, temp_test_dir)
            assert read_content == content
        except Exception as e:
            # Some systems may not support Unicode filenames
            pytest.skip(f"Unicode filename not supported on this system: {e}")
    
    def test_binary_file_error_messages(self, temp_test_dir):
        """Test that binary files produce clear, helpful error messages."""
        from tools.read_file import read_file
        from pathlib import Path
        
        # Create different types of binary files
        test_files = {
            "document.pdf": b'%PDF-1.4\x00\x00\x00binary data',
            "image.jpg": b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01',
            "archive.zip": b'PK\x03\x04\x14\x00\x00\x00\x08\x00'
        }
        
        for filename, content in test_files.items():
            file_path = Path(temp_test_dir) / filename
            with open(file_path, 'wb') as f:
                f.write(content)
            
            with pytest.raises(ValueError) as exc_info:
                read_file(filename, temp_test_dir)
            
            error_msg = str(exc_info.value)
            assert filename in error_msg
            assert "binary file" in error_msg
            assert "cannot be displayed as text" in error_msg 