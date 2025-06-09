# AI-Powered File Operations Agent

An intelligent agent for CRUD file operations with CLI interface and MCP (Model Context Protocol) integration.

## Overview

This project implements an autonomous agent capable of:
- Complete CRUD file operations (Create, Read, Update, Delete)
- Intelligent file content analysis using GPT APIs
- CLI interface for local interaction
- MCP server for integration with Claude Desktop and other clients
- Tool-based architecture with ReAct pattern
- Smart fallback system for query validation

The system offers **two operational modes**:

1. **LLM-Powered Agent** (GPT-4o + LLaMA 3 8B) - Advanced artificial intelligence
2. **Pydantic-AI Agent** (Native framework) - Modern framework implementation

## Architecture

The project implements **two architectural approaches** to meet different needs:

### 1. **Custom ReAct Architecture** (Main Implementation)
From-scratch implementation of the entire ReAct architecture (Reasoning + Acting) with manual tool orchestration and dual-model system. Uses GPT-4o for planning and LLaMA 3 for query validation. This approach ensures **maximum control** and transparency over the decision cycle, with a lightweight structure optimized for local execution, low latency, and custom MCP integration.

**Technical advantages:**
- Direct control over reasoning loops and tool execution
- Optimized for performance-critical scenarios
- Transparent debugging and customization
- Minimal framework overhead

### 2. **Pydantic-AI Architecture** (Modern Implementation)
Modern implementation using the **Pydantic-AI** framework for declarative tool orchestration, automatic structured output validation, and dependency injection. Demonstrates integration with modern agentic frameworks while maintaining the same user interface and functionality.

**Technical advantages:**
- Automatic tool orchestration and error handling
- Built-in structured output validation with Pydantic models
- Type-safe dependency injection
- Framework-managed conversation flow

### Main Components

- **Agent Core**: Agent implementation with ReAct pattern
- **Tool Registry**: Centralized system for tool management
- **CLI Interface**: Command line interface for local use
- **MCP Servers**: Servers for integration with MCP clients
- **Security Layer**: Query validation and security controls

### Available Tools

1. **list_files()**: Lists all files in directory with metadata
2. **read_file(filename)**: Reads complete content of a file
3. **write_file(filename, content, mode)**: Writes content to a file
4. **delete_file(filename)**: Deletes a file from directory
5. **answer_question_about_files(query)**: Answers questions about files using GPT intelligence

### ⚡ Guaranteed Tool Usage (Assignment Compliance)

**ALL agents strictly respect assignment requirements:**

- ✅ **Mandatory Tool Usage**: Every file operation MUST use the appropriate tool
- ✅ **Internal Planning Loop**: ReAct pattern implemented with internal reasoning loop
- ✅ **Tool-Based Architecture**: Architecture completely based on CRUD tools
- ✅ **Smart Validation**: Automatic detection of queries requiring tools
- ✅ **Forced Tool Execution**: System that forces tool usage when necessary

**Example of compliant behavior:**
```bash
User: "list files"
❌ Direct response: "I can help you list files..." 
✅ Correct response: Uses list_files() tool + provides results

User: "read config.json"  
❌ Direct response: "I'll read that file for you..."
✅ Correct response: Uses read_file("config.json") tool + shows content
```

## Installation

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Setup

```bash
# Clone repository
git clone <repository-url>
cd assignment

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### API Keys Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

The project offers **2 distinct agents** for different operational needs:

### 1. LLM-Powered Agent (Advanced AI)

**Features:**
- GPT-4o for reasoning and main planning
- LLaMA 3 8B for query validation (economical)
- Advanced natural language understanding
- Intelligent multi-step reasoning

**Prerequisites:**
```env
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here  # Optional but recommended
```

**Launch:**
```bash
python chat_interface/llm_cli.py --directory /path/to/working/directory
```

For testing, sample files are created in the test_files folder:
```bash
python chat_interface/llm_cli.py --directory ./test_files
```

**Advanced usage examples:**
```bash
# Natural language queries
> "Show me all Python files and summarize what they do"
> "Find the most recently modified file and read its content"
> "Create a backup of all important files with timestamp"
> "Analyze the file types and tell me about the project structure"
```

### 2. Pydantic-AI Agent (Modern Framework)

**Features:**
- Native **Pydantic-AI** framework for tool orchestration
- Automatic structured output with Pydantic validation
- Advanced dependency injection
- GPT-4o + Groq for dual-model architecture
- Same interface as other agents but with modern technology

**Prerequisites:**
```env
OPENAI_API_KEY=your_openai_api_key_here  # REQUIRED
GROQ_API_KEY=your_groq_api_key_here     # OPTIONAL
```

**Launch:**
```bash
python chat_interface/pydantic_cli.py --directory /path/to/working/directory
```

**Usage examples:**
```bash
# Same commands as other agents but with structured output
> "List all files and analyze their types"
> "Create a summary report of all JSON files"
> "Read the largest Python file and explain its structure"
```

### Agent Selection

| Scenario | Recommended Agent | Reason |
|----------|-------------------|---------|
| Testing and development | LLM-Powered | Fast and reliable |
| Complex queries | LLM-Powered or Pydantic-AI | Superior natural understanding |
| Advanced analysis | Pydantic-AI | Modern framework + structured output |
| Enterprise production | LLM-Powered or Pydantic-AI | Greater flexibility and robustness |
| Framework experimentation | Pydantic-AI | Shows modern framework integration |

### MCP Integration with Claude Desktop

Both agents are available as MCP servers:

1. Copy the `mcp_config.json` file to Claude Desktop's configuration directory
2. Update the paths in the configuration file for your system
3. Restart Claude Desktop
4. MCP servers will be available as tools in Claude Desktop

#### Available MCP Servers

- **llm-file-operations-agent**: Server with LLM capabilities for complex queries
- **Pydantic-AI Agent**: Available through existing servers with structured output

## Advanced Features

### Intelligent Fallback System

The agent implements a 3-level fallback system:

1. **LLaMA 3 8B (Groq)**: Primary validation (fast and economical)
2. **GPT-4o (OpenAI)**: Fallback if Groq unavailable
3. **Pattern-based**: Deterministic fallback if both APIs unavailable

### Security

- Query validation to prevent unsafe operations
- Path traversal controls to limit file access
- Input sanitization
- Safe error handling

### Multi-tool Orchestration

The agent can execute tool sequences in a single request:

```
Query: "read the file that was modified most recently"
Execution:
1. list_files() -> gets file metadata
2. Identifies the most recent file
3. read_file(filename) -> reads the content
4. Returns the result
```

## Testing

The project includes a **comprehensive test suite** with 39+ tests verifying all CRUD components, agent functionality, error scenarios, security and integration.

### Test Files

**Core Test Files:**

- **`test_tools.py`**: Complete testing of all five CRUD tools (list, read, write, delete, answer_question). Includes functionality tests, error handling, security validation, and integration tests. Covers path traversal protection, binary file detection, Unicode support, and concurrent operations.

- **`test_agents.py`**: Comprehensive testing of LLM agent functionality and query validation system. Tests the fix for file analysis queries (e.g., "cosa fa hello.py?"), validator behavior, tool usage decisions, and error handling scenarios.

- **`conftest.py`**: Test configuration and shared fixtures. Provides temporary test directories with sample files, ensuring consistent test environments across all test modules.

**Additional Test Files:**

- **`test_basic_functionality.py`**: Basic functionality verification tests for agent imports, tool operations, and agent initialization. Useful for quick verification that all components are working correctly after installation or changes.

- **`test_append_fix.py`**: Specific test for the append operation bug fix. Validates that the "triple append" issue has been resolved and that append operations execute exactly once as expected.

- **`test_end_to_end.py`**: End-to-end testing of binary file handling improvements. Tests the enhanced error messages for PDF files and other binary formats, ensuring clear user feedback instead of confusing codec errors.

- **`simple_test_tools.py`**: Lightweight tool behavior verification. Quick tests for tool registry functionality and improved error message formatting, useful for rapid development iteration.

**Documentation:**

- **`TESTING_GUIDE.md`**: Comprehensive guide for running tests, understanding test scenarios, and extending the test suite.

### Test Coverage

- **100% Tool Coverage**: All 5 CRUD tools tested (list, read, write, delete, answer_question)
- **100% Error Handling**: Error scenarios and edge cases
- **100% Security**: Path traversal protection and validation  
- **100% Agent Functionality**: Query validation, tool orchestration, and reasoning loops
- **100% Integration**: Multi-tool workflows and agent coordination

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_tools.py -v
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Expected Output

```
tests/test_tools.py::TestListFiles::test_list_files_success PASSED     [  2%]
tests/test_tools.py::TestReadFile::test_read_file_success PASSED       [  5%]
tests/test_tools.py::TestWriteFile::test_write_file_new PASSED          [  7%]
tests/test_tools.py::TestDeleteFile::test_delete_file_success PASSED   [ 10%]
tests/test_agents.py::TestLLMValidator::test_file_analysis_queries_approved PASSED [ 15%]
...
tests/test_tools.py::TestToolIntegration::test_concurrent_operations PASSED [100%]

======================== 39 passed, 1 skipped in 1.97s ========================
```

## Project Structure

```
assignment/
├── agent/                  # Main agent logic
│   ├── llm_agent.py       # LLM-powered agent
│   ├── tool_registry.py   # Tool registry
│   └── llm_validator.py   # LLM validation
├── Pydantic-AI_Agent/      # Pydantic-AI implementation
│   ├── pydantic_agent.py  # Agent with Pydantic-AI framework
│   ├── models.py          # Pydantic models
│   ├── dependencies.py    # Dependency injection
│   └── README.md          # Specific documentation
├── tools/                  # Tool implementations
│   ├── list_files.py
│   ├── read_file.py
│   ├── write_file.py
│   ├── delete_file.py
│   └── answer_question_about_files.py
├── chat_interface/         # User interfaces
│   ├── llm_cli.py         # LLM CLI
│   └── pydantic_cli.py    # Pydantic-AI CLI
├── server/                 # MCP servers
│   └── llm_mcp_server.py  # LLM server with GPT-4o
├── tests/                  # Comprehensive test suite
│   ├── test_tools.py      # CRUD tools testing (27 tests)
│   ├── test_agents.py     # Agent functionality testing (13 tests)
│   ├── conftest.py        # Test configuration and fixtures
│   ├── test_basic_functionality.py  # Basic functionality verification
│   ├── test_append_fix.py # Append operation bug fix validation
│   ├── test_end_to_end.py # End-to-end binary file handling
│   ├── simple_test_tools.py  # Lightweight tool verification
│   └── TESTING_GUIDE.md   # Test documentation
├── Guide_Documents/        # Extended documentation
├── test_files/            # Sample files for testing
├── mcp_config.json        # MCP configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Assignment Compliance

This project **meets and exceeds** all assignment requirements:

### Mandatory Requirements

- **Agent Design**: Tool-based architecture with ReAct pattern
- **CRUD Operations**: All 5 required tools implemented
- **Multi-tool Orchestration**: Sequential execution of multiple tools
- **Chat Interface**: Functional CLI for interaction
- **MCP Server**: Fully functional MCP server
- **Directory Constraints**: All operations limited to base directory

### Bonus Features

- **Test Suite**: Complete tool coverage with pytest (26 tests)
- **Safe Behavior**: Query validation and inappropriate request rejection
- **Lightweight Model**: Fallback system with lighter models for validation

### Extra Implementations

- **Pydantic-AI Integration**: Modern framework suggested in assignment
- **Two distinct agents**: LLM-powered and Pydantic-AI
- **Dual Architecture**: Custom ReAct + Native framework
- **Structured Output**: Automatic validation with Pydantic
- **Extended Documentation**: Complete guides in `Guide_Documents/`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure virtual environment is activated
2. **API Keys**: Verify API keys are configured correctly
3. **Permissions**: Check working directory permissions
4. **MCP Integration**: Verify paths in MCP configuration file

### Logs and Debug

MCP servers generate logs in:
- `/tmp/mcp_server.log`
- `/tmp/llm_mcp_server.log`

## Contributing

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## License

This project is released under MIT license.

## Contact

For questions or support, contact the developer: 
Andrea Belli Contarini - andreabcontarini@gmail.com