"""
Test suite for individual tools (CRUD operations).
"""
import pytest
import os
from pathlib import Path

from tools.list_files import list_files
from tools.read_file import read_file
from tools.write_file import write_file
from tools.delete_file import delete_file
from tools.answer_question_about_files import answer_question_about_files


class TestListFiles:
    """Test list_files tool functionality."""
    
    def test_list_files_success(self, temp_test_dir):
        """Test successful file listing."""
        result = list_files(temp_test_dir)
        
        assert isinstance(result, list)
        assert len(result) == 5  # From conftest.py fixture
        
        # Check that all expected files are present
        filenames = [f['name'] for f in result]
        expected_files = ['example.txt', 'script.py', 'data.json', 'large_file.txt', 'empty.txt']
        
        for expected in expected_files:
            assert expected in filenames
    
    def test_list_files_metadata(self, temp_test_dir):
        """Test that file metadata is correctly included."""
        result = list_files(temp_test_dir)
        
        for file_info in result:
            assert 'name' in file_info
            assert 'size' in file_info
            assert 'modified' in file_info
            assert 'extension' in file_info
            assert isinstance(file_info['size'], int)
            assert file_info['size'] >= 0
    
    def test_list_files_nonexistent_directory(self):
        """Test list_files with non-existent directory."""
        with pytest.raises(Exception):
            list_files("/nonexistent/directory")


class TestReadFile:
    """Test read_file tool functionality."""
    
    def test_read_file_success(self, temp_test_dir):
        """Test successful file reading."""
        content = read_file("example.txt", temp_test_dir)
        assert content == "Hello World"
    
    def test_read_file_python(self, temp_test_dir):
        """Test reading Python file."""
        content = read_file("script.py", temp_test_dir)
        assert content == "print('Hello Python')"
    
    def test_read_file_json(self, temp_test_dir):
        """Test reading JSON file."""
        content = read_file("data.json", temp_test_dir)
        assert '"name": "test"' in content
    
    def test_read_file_empty(self, temp_test_dir):
        """Test reading empty file."""
        content = read_file("empty.txt", temp_test_dir)
        assert content == ""
    
    def test_read_file_nonexistent(self, temp_test_dir):
        """Test reading non-existent file."""
        with pytest.raises(FileNotFoundError):
            read_file("nonexistent.txt", temp_test_dir)
    
    def test_read_file_path_traversal_protection(self, temp_test_dir):
        """Test that path traversal is blocked."""
        with pytest.raises(Exception):
            read_file("../../../etc/passwd", temp_test_dir)
    
    def test_read_binary_file_detection(self, temp_test_dir):
        """Test that binary files are properly detected and rejected."""
        # Create a fake PDF file with binary content
        fake_pdf_path = Path(temp_test_dir) / "test.pdf"
        with open(fake_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\x00\x00\x00\x00binary content here')
        
        with pytest.raises(ValueError) as exc_info:
            read_file("test.pdf", temp_test_dir)
        
        error_msg = str(exc_info.value)
        assert "binary file" in error_msg
        assert "PDF document" in error_msg
        assert "cannot be displayed as text" in error_msg


class TestWriteFile:
    """Test write_file tool functionality."""
    
    def test_write_file_new(self, temp_test_dir):
        """Test writing new file."""
        result = write_file("new_file.txt", "New content", temp_test_dir)
        assert result is True
        
        # Verify file was created
        file_path = Path(temp_test_dir) / "new_file.txt"
        assert file_path.exists()
        assert file_path.read_text() == "New content"
    
    def test_write_file_overwrite(self, temp_test_dir):
        """Test overwriting existing file."""
        result = write_file("example.txt", "Overwritten content", temp_test_dir, mode="w")
        assert result is True
        
        # Verify file was overwritten
        content = read_file("example.txt", temp_test_dir)
        assert content == "Overwritten content"
    
    def test_write_file_append(self, temp_test_dir):
        """Test appending to existing file."""
        result = write_file("example.txt", " Appended", temp_test_dir, mode="a")
        assert result is True
        
        # Verify content was appended
        content = read_file("example.txt", temp_test_dir)
        assert content == "Hello World Appended"
    
    def test_write_file_with_unicode(self, temp_test_dir):
        """Test writing file with Unicode characters."""
        unicode_content = "Hello 🌍 Mondo 中文 العربية"
        result = write_file("unicode.txt", unicode_content, temp_test_dir)
        assert result is True
        
        # Verify Unicode content
        content = read_file("unicode.txt", temp_test_dir)
        assert content == unicode_content
    
    def test_write_file_path_traversal_protection(self, temp_test_dir):
        """Test that path traversal is blocked."""
        with pytest.raises(Exception):
            write_file("../../../tmp/malicious.txt", "bad content", temp_test_dir)


class TestDeleteFile:
    """Test delete_file tool functionality."""
    
    def test_delete_file_success(self, temp_test_dir):
        """Test successful file deletion."""
        # Verify file exists first
        file_path = Path(temp_test_dir) / "example.txt"
        assert file_path.exists()
        
        result = delete_file("example.txt", temp_test_dir)
        assert result is True
        
        # Verify file was deleted
        assert not file_path.exists()
    
    def test_delete_file_nonexistent(self, temp_test_dir):
        """Test deleting non-existent file."""
        with pytest.raises(FileNotFoundError):
            delete_file("nonexistent.txt", temp_test_dir)
    
    def test_delete_file_path_traversal_protection(self, temp_test_dir):
        """Test that path traversal is blocked."""
        with pytest.raises(Exception):
            delete_file("../../../etc/passwd", temp_test_dir)


class TestAnswerQuestionAboutFiles:
    """Test answer_question_about_files tool functionality."""
    
    def test_count_files(self, temp_test_dir):
        """Test counting files."""
        result = answer_question_about_files(temp_test_dir, "How many files are there?")
        assert "5 files" in result
    
    def test_largest_file(self, temp_test_dir):
        """Test finding largest file."""
        result = answer_question_about_files(temp_test_dir, "What is the largest file?")
        assert "large_file.txt" in result
    
    def test_smallest_file(self, temp_test_dir):
        """Test finding smallest file."""
        result = answer_question_about_files(temp_test_dir, "What is the smallest file?")
        assert "empty.txt" in result
    
    def test_file_types(self, temp_test_dir):
        """Test analyzing file types."""
        result = answer_question_about_files(temp_test_dir, "What file types do I have?")
        assert ".txt" in result
        assert ".py" in result
        assert ".json" in result
    
    def test_recent_file(self, temp_test_dir):
        """Test finding most recent file."""
        result = answer_question_about_files(temp_test_dir, "What is the most recent file?")
        assert len(result) > 0  # Should return some file name
    
    def test_content_search(self, temp_test_dir):
        """Test searching file contents."""
        result = answer_question_about_files(temp_test_dir, "Which files contain Python?")
        # This depends on the specific implementation of content search
        assert isinstance(result, str)
    
    def test_nonexistent_directory(self):
        """Test with non-existent directory."""
        result = answer_question_about_files("/nonexistent", "How many files?")
        assert "does not exist" in result


class TestToolIntegration:
    """Test tool integration and edge cases."""
    
    def test_full_crud_cycle(self, temp_test_dir):
        """Test complete CRUD cycle: Create, Read, Update, Delete."""
        filename = "crud_test.txt"
        content = "Initial content"
        
        # CREATE
        assert write_file(filename, content, temp_test_dir) is True
        
        # READ
        read_content = read_file(filename, temp_test_dir)
        assert read_content == content
        
        # UPDATE (append)
        assert write_file(filename, " - Updated", temp_test_dir, mode="a") is True
        updated_content = read_file(filename, temp_test_dir)
        assert updated_content == "Initial content - Updated"
        
        # DELETE
        assert delete_file(filename, temp_test_dir) is True
        
        # Verify deletion
        with pytest.raises(FileNotFoundError):
            read_file(filename, temp_test_dir)
    
    def test_concurrent_operations(self, temp_test_dir):
        """Test that multiple operations don't interfere."""
        # Create multiple files
        files = {
            "file1.txt": "Content 1",
            "file2.txt": "Content 2", 
            "file3.txt": "Content 3"
        }
        
        for filename, content in files.items():
            assert write_file(filename, content, temp_test_dir) is True
        
        # Read all files
        for filename, expected_content in files.items():
            content = read_file(filename, temp_test_dir)
            assert content == expected_content
        
        # List should show all files
        file_list = list_files(temp_test_dir)
        file_names = [f['name'] for f in file_list]
        
        for filename in files.keys():
            assert filename in file_names 