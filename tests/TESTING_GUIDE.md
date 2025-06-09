# Testing Guide

Complete guide to understand and run File Operations Agent tests.

## Overview

The project's test suite is designed to ensure quality and reliability of all CRUD components and advanced agent features. Tests cover success scenarios, error handling, edge cases, and security.

## Test Suite Structure

### Main Files

#### `conftest.py`
Pytest configuration file that defines shared fixtures for all tests.

**Available Fixtures:**
- `temp_test_dir`: Creates a temporary directory with pre-configured test files
- `agent`: Deterministic agent instance for testing
- `llm_agent`: Custom ReAct Agent instance (requires API keys)
- `sample_files_content`: Sample content for custom tests

**Pre-configured Test Files:**
```
temp_test_dir/
├── example.txt (11 bytes) - "Hello World"
├── script.py (21 bytes) - "print('Hello Python')"
├── data.json (30 bytes) - '{"name": "test", "value": 123}'
├── large_file.txt (61 bytes) - Longer content for testing
└── empty.txt (0 bytes) - Empty file
```

#### `test_tools.py`
Comprehensive tests for all CRUD tools and advanced features.

**Test Classes:**

1. **TestListFiles** (3 tests)
   - Verifies correct file listing
   - Metadata validation (name, size, modification date, extension)
   - Non-existent directory handling

2. **TestReadFile** (6 tests)
   - Reading different file types (.txt, .py, .json)
   - Empty files
   - Non-existent files (error)
   - Path traversal protection

3. **TestWriteFile** (5 tests)
   - Creating new files
   - Overwriting existing files
   - Append mode
   - Unicode support
   - Path traversal protection

4. **TestDeleteFile** (3 tests)
   - Deleting existing files
   - Non-existent files (error)
   - Path traversal protection

5. **TestAnswerQuestionAboutFiles** (7 tests)
   - File counting
   - Largest/smallest file identification
   - File type analysis
   - Most recent file search
   - Content searching
   - Non-existent directory handling

6. **TestToolIntegration** (2 tests)
   - Complete CRUD cycle
   - Concurrent operations

## Running Tests

### Basic Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific tests
python -m pytest tests/test_tools.py::TestListFiles -v

# Tests with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Quiet mode tests
python -m pytest tests/ -q
```

### Tool-Specific Tests

```bash
# Test only list operations
python -m pytest tests/ -k "list" -v

# Test only write operations
python -m pytest tests/ -k "write" -v

# Test only security
python -m pytest tests/ -k "traversal" -v

# Test integration
python -m pytest tests/ -k "integration" -v
```

### Expected Output

```
tests/test_tools.py::TestListFiles::test_list_files_success PASSED     [  3%]
tests/test_tools.py::TestListFiles::test_list_files_metadata PASSED    [  7%]
...
tests/test_tools.py::TestToolIntegration::test_concurrent_operations PASSED [100%]

======================== 26 passed in 0.32s ========================
```

## Test Coverage

### Tested Scenarios

**✅ Basic Operations:**
- List files with complete metadata
- Read files of different formats
- Write with write/append modes
- Delete existing files

**✅ Error Handling:**
- Non-existent files/directories
- Invalid paths
- Encoding issues
- Permission errors

**✅ Security:**
- Path traversal protection (`../../../etc/passwd`)
- Input validation
- Base directory confinement

**✅ Edge Cases:**
- Empty files
- Unicode content
- Large files
- Multiple operations

**✅ Integration:**
- Complete CRUD cycles
- Sequential operations
- Data consistency

### Coverage Metrics

- **Tool Coverage**: 100% (all 5 CRUD tools)
- **Error Paths**: 100% (all error types)
- **Security Cases**: 100% (path traversal, validation)
- **Integration**: 100% (multi-tool workflows)

## Test Debugging

### Verbose Testing

```bash
# Detailed output with reasoning
python -m pytest tests/ -v -s

# Show print statements
python -m pytest tests/ -v -s --capture=no

# Stop at first failure
python -m pytest tests/ -x
```

### Individual Tests

```bash
# Specific test with debug
python -m pytest tests/test_tools.py::TestDeleteFile::test_delete_file_success -v -s
```

### Fixture Debugging

For fixture debugging, modify `conftest.py`:

```python
@pytest.fixture
def temp_test_dir():
    temp_dir = tempfile.mkdtemp()
    print(f"DEBUG: Created temp dir: {temp_dir}")  # Debug line
    # ... rest of code
```

## Extending Test Suite

### Adding New Tests

1. **For new tool:**
   ```python
   class TestNewTool:
       def test_new_tool_success(self, temp_test_dir):
           result = new_tool("param", temp_test_dir)
           assert result == expected
   ```

2. **For error scenarios:**
   ```python
   def test_new_tool_error(self, temp_test_dir):
       with pytest.raises(SpecificError):
           new_tool("invalid_param", temp_test_dir)
   ```

3. **For integration:**
   ```python
   def test_new_tool_integration(self, temp_test_dir):
       # Multi-step test
       step1_result = tool1(temp_test_dir)
       step2_result = tool2(step1_result, temp_test_dir)
       assert step2_result == expected
   ```

### Custom Fixtures

```python
@pytest.fixture
def custom_test_setup():
    # Custom setup for specific tests
    setup_data = create_custom_setup()
    yield setup_data
    # Cleanup
    cleanup_custom_setup(setup_data)
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("test1.txt", True),
    ("test2.json", True),
    ("nonexistent.txt", False),
])
def test_file_operations(self, temp_test_dir, input, expected):
    result = operation(input, temp_test_dir)
    assert result == expected
```

## Performance Testing

### Timing Tests

```python
import time

def test_large_file_performance(self, temp_test_dir):
    start = time.time()
    result = read_large_file(temp_test_dir)
    duration = time.time() - start
    
    assert duration < 1.0  # Should complete in < 1 second
    assert result is not None
```

### Memory Tests

```python
import psutil
import os

def test_memory_usage(self, temp_test_dir):
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform operation
    result = memory_intensive_operation(temp_test_dir)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable
    assert memory_increase < 50 * 1024 * 1024  # < 50MB
```

## Continuous Integration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Local CI Simulation

```bash
# Test on multiple Python versions (if available)
python3.8 -m pytest tests/
python3.9 -m pytest tests/
python3.10 -m pytest tests/
python3.11 -m pytest tests/

# Generate coverage report
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Troubleshooting

### Common Issues

1. **Import Errors:**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   python -m pytest tests/
   ```

2. **API Key Tests:**
   ```bash
   # Skip API-dependent tests
   python -m pytest tests/ -m "not requires_api"
   
   # Or set environment variables
   export OPENAI_API_KEY="your_key"
   export GROQ_API_KEY="your_key"
   ```

3. **Permission Issues:**
   ```bash
   # Ensure write permissions
   chmod +w test_files/
   python -m pytest tests/
   ```

4. **Temporary Directory Issues:**
   ```bash
   # Clean up temp directories
   find /tmp -name "tmp*" -type d -delete
   python -m pytest tests/
   ```

### Logging Configuration

```python
# In conftest.py or test files
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in test function
def test_with_logging(self, caplog):
    with caplog.at_level(logging.INFO):
        result = function_under_test()
        assert "Expected log message" in caplog.text
``` 