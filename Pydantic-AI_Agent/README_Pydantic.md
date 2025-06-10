# Pydantic-AI Agent Implementation

Modern agent implementation using the **Pydantic-AI** framework with structured output and type-safe operations.

## Core Features

- **Structured Output**: All responses validated with Pydantic models
- **Type-Safe Operations**: Automatic parameter validation and dependency injection
- **Dual-Model Architecture**: GPT-4o for operations, optional Groq for validation
- **Native Tool Orchestration**: Framework-managed tool execution

## Key Differences from Custom ReAct Agent

| Aspect | Custom ReAct | Pydantic-AI |
|--------|--------------|-------------|
| **Tool Management** | Custom registry | Native framework tools |
| **Validation** | Manual parameter checks | Automatic type validation |
| **Error Handling** | Custom implementation | Framework-managed |
| **Orchestration** | Manual tool coordination | Declarative tool execution |

## Quick Start

```bash
# Launch Pydantic-AI agent
python chat_interface/pydantic_cli.py --directory ./test_files
```

### Programmatic Usage

```python
from Pydantic-AI_Agent.pydantic_agent import PydanticFileAgent

agent = PydanticFileAgent(
    base_directory="/path/to/files",
    openai_api_key="sk-...",
    groq_api_key="gsk_...",  # Optional
)

response = await agent.process_query("List all files")
print(f"Success: {response.success}")
print(f"Message: {response.message}")
```

## Structured Output Model

All responses follow the `AgentResponse` Pydantic model:

```python
class AgentResponse(BaseModel):
    success: bool
    message: str
    type: str
    files: Optional[List[Dict[str, Any]]] = None
    file_content: Optional[str] = None
    analysis_result: Optional[str] = None
    operations_performed: Optional[List[str]] = None
    reasoning: Optional[str] = None
```

## API Requirements

- **OpenAI API Key**: Required for GPT-4o operations
- **Groq API Key**: Optional for query validation

## Testing

The Pydantic-AI agent is tested within the main test suite:

```bash
python -m pytest tests/test_agents.py::TestPydanticAgent -v
```

Includes tests for:
- Agent initialization and configuration
- All CRUD operations with structured output
- Error handling with Pydantic validation
- Type-safe parameter validation

## Framework Benefits

### Type Safety
- Automatic parameter validation with Pydantic models
- Compile-time error detection for tool parameters
- Structured response objects with guaranteed schemas

### Error Handling
```python
# Structured error responses
AgentResponse(
    success=False,
    message="File 'nonexistent.txt' not found",
    type="error",
    reasoning="File operation failed"
)
```

### Extension Example
```python
@agent.file_operations_agent.tool
async def custom_tool(
    ctx: RunContext[AgentDependencies],
    param: str
) -> str:
    """Custom tool with automatic validation."""
    return f"Processed: {param}"
```

This implementation demonstrates modern agentic patterns with structured output and type safety while maintaining full compatibility with the existing tool interfaces. 