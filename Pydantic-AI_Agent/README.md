# Pydantic-AI Hybrid Agent

Hybrid agent implementation for file operations using the **Pydantic-AI** framework with dual-model architecture.

## Objective

This module implements a hybrid system that combines:

- **OpenAI GPT-4o**: File operations and advanced reasoning
- **Groq llama-3.1-8b-instant**: Query validation and security (optional)
- **Pydantic-AI Framework**: Native tool orchestration and structured output

## Architecture

### Main Components

1. **`PydanticFileAgent`** - Main agent with hybrid architecture
2. **`AgentDependencies`** - Type-safe dependency injection
3. **`AgentResponse`** - Structured output with Pydantic validation
4. **Dual-Model System** - GPT-4o for operations, Groq for validation

### Processing Flow

```
User Query
    ↓
[Optional] Groq Validation (SAFE/DANGEROUS)
    ↓
GPT-4o File Operations (with tools)
    ↓
Structured AgentResponse
```

### Comparison with Previous Implementations

| Aspect | Original Implementation | Pydantic-AI Hybrid |
|--------|-------------------------|-------------------|
| **Architecture** | Single model custom planner | Dual-model hybrid system |
| **Tool Registry** | Custom ToolRegistry | Native Pydantic-AI tools |
| **Output** | Unstructured Dict | Structured Pydantic models |
| **Validation** | Manual validation | Automatic + security layer |
| **Orchestration** | Manual step-by-step | Declarative + intelligent routing |
| **Security** | Basic input validation | Dedicated validation model |

## Usage

### Interactive CLI

```bash
cd agent_pydantic
python pydantic_cli.py --create-samples -d ./test_files
```

The CLI supports:
- Interactive API configuration (OpenAI required, Groq optional)
- Special commands (`/help`, `/status`, `/verbose`, etc.)
- Natural language queries
- Verbose mode for debugging

### Programmatic Usage

```python
import asyncio
from pydantic_agent import PydanticFileAgent

async def main():
    # Initialize hybrid agent
    agent = PydanticFileAgent(
        base_directory="/path/to/files",
        openai_api_key="sk-...",
        groq_api_key="gsk_...",  # Optional
        verbose=True
    )
    
    # Execute query with structured output
    response = await agent.process_query("List all files and tell me which is the largest")
    
    print(f"Success: {response.success}")
    print(f"Message: {response.message}")
    print(f"Type: {response.type}")
    if response.files:
        print(f"Files found: {len(response.files)}")

asyncio.run(main())
```

## Available Tools

All tools are implemented as native Pydantic-AI tools:

- **`list_files_tool()`** - List files with complete metadata
- **`read_file_tool(filename, encoding)`** - Read file content
- **`write_file_tool(filename, content, mode, encoding)`** - Write/create file
- **`delete_file_tool(filename)`** - Delete file
- **`answer_question_tool(query)`** - Intelligent file analysis

### Tool Features

- **Automatic validation** of parameters with Pydantic
- **Robust error handling** with detailed messaging
- **Type-safe dependency injection**
- **Configurable logging** for debugging

## Structured Output

The agent always returns a validated `AgentResponse`:

```python
class AgentResponse(BaseModel):
    success: bool
    message: str
    type: str
    
    # Optional data
    files: Optional[List[Dict[str, Any]]] = None
    file_content: Optional[str] = None
    analysis_result: Optional[str] = None
    operations_performed: Optional[List[str]] = None
    reasoning: Optional[str] = None
```

## Configuration

### Required API Keys

- **OpenAI API Key**: Required for GPT-4o (file operations)
- **Groq API Key**: Optional for llama-3.1-8b-instant (validation)

### Supported Models

#### File Operations (Required)
- **OpenAI GPT-4o**: Main model for file operations

#### Validation (Optional)
- **Groq llama-3.1-8b-instant**: Query validation for security

## Security

### Validation Layer

If configured, Groq provides a security layer that:
- Analyzes user queries before execution
- Classifies as SAFE or DANGEROUS
- Blocks potentially dangerous operations
- Prevents path traversal and system commands

### Fallback Mechanism

- If Groq is unavailable: proceeds directly with GPT-4o
- If Groq fails: continues processing with error logging
- No service interruption for validation issues

## Testing and Examples

### CLI Testing

```bash
# Test with sample files
python pydantic_cli.py --create-samples -d ./test_files

# Test common queries
> list all files
> read config.json
> create a file test.txt with content Hello World
> delete old.txt
> analyze all Python files
```

### Example Queries

- "List all files in the directory"
- "Read the content of config.json" 
- "Create a file called test.txt with content Hello World"
- "Delete the file old.txt"
- "What is the largest file in the directory?"
- "Analyze all Python files and tell me what they do"

## Multi-Step Reasoning

The GPT-4o agent automatically handles complex tasks:

```python
# Complex query automatically decomposed
response = await agent.process_query(
    "Count the files, then read the most recent one and summarize it"
)

# The agent automatically:
# 1. Calls list_files_tool() to count files
# 2. Analyzes metadata to find the most recent file  
# 3. Calls read_file_tool() to read content
# 4. Generates content summary
# 5. Returns structured response
```

## Hybrid Architecture Benefits

### 1. Enhanced Security
- Dedicated validation layer with Groq
- Prevention of dangerous operations
- Graceful fallback when validation unavailable

### 2. Structured Output
- Automatic Pydantic validation
- Type-safe responses
- Consistent output format
- Reduced parsing errors

### 3. Modern Framework Integration
- Native Pydantic-AI tool support
- Declarative tool orchestration
- Dependency injection system
- Automatic error handling

### 4. Performance Optimization
- Fast validation with llama-3.1-8b-instant
- Intelligent model routing
- Optional validation for speed
- Efficient tool coordination

## Error Handling

### Graceful Degradation

```python
# If validation model fails
response = await agent.process_query("dangerous query")
# → Continues with GPT-4o but logs warning

# If file operation fails
response = await agent.process_query("read nonexistent.txt")
# → Returns structured error with details
```

### Error Response Structure

```python
AgentResponse(
    success=False,
    message="File 'nonexistent.txt' not found in directory",
    type="error",
    reasoning="Attempted file read operation failed"
)
```

## Development and Extension

### Adding New Tools

```python
@agent.file_operations_agent.tool
async def custom_tool(
    ctx: RunContext[AgentDependencies],
    param: str
) -> str:
    """Custom tool implementation."""
    try:
        # Tool logic using ctx.deps
        result = custom_operation(param, ctx.deps.base_directory)
        return result
    except Exception as e:
        raise Exception(f"Custom tool failed: {str(e)}")
```

### Custom Response Types

```python
class CustomResponse(BaseModel):
    success: bool
    custom_field: str
    custom_data: Optional[Dict[str, Any]] = None

# Use in agent initialization
agent = Agent(
    model=openai_model,
    deps_type=AgentDependencies,
    result_type=CustomResponse,  # Custom response type
    system_prompt=custom_prompt
)
```

## Integration

### MCP Server

The Pydantic-AI agent can be exposed via MCP server:

```python
# Available in server/pydantic_mcp_server.py (if implemented)
# Provides same MCP interface as other agents
```

### API Endpoints

```python
from fastapi import FastAPI
from pydantic_agent import PydanticFileAgent

app = FastAPI()
agent = PydanticFileAgent(...)

@app.post("/query")
async def process_query(query: str):
    response = await agent.process_query(query)
    return response.dict()
```

This hybrid implementation showcases modern agentic patterns with structured output, type safety, and intelligent model routing while maintaining compatibility with the original tool interfaces. 