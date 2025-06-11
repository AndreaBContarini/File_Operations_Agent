# MCP Guide (Model Context Protocol)

Comprehensive guide for integrating the File Operations Agent with MCP clients like Claude Desktop and Cursor.

## MCP Overview

The Model Context Protocol (MCP) is an open standard that allows AI assistants to securely connect to data sources and external tools. Our File Operations Agent exposes its functionality through an MCP server:

- **LLM Server** (`llm_mcp_server.py`): Advanced operations with LLM reasoning capabilities and GPT-4o

## MCP Architecture

```

MCP Client (Claude Desktop/Cursor)
↓ JSON-RPC 2.0
MCP Server (File Operations Agent)
↓ Tool Registry
Tool Implementation (CRUD Operations)
↓ File System
Working Directory

````

## Configuration

### Configuration File

The `mcp_config.json` file defines the available MCP servers:

```json
{
  "mcpServers": {
    "llm-file-operations-agent": {
      "command": "/path/to/.venv/bin/python",
      "args": [
        "/path/to/assignment/server/llm_mcp_server.py",
        "--directory",
        "/path/to/work_directory",
        "--name",
        "llm-file-operations-agent"
      ],
      "env": {
        "PYTHONPATH": "/path/to/assignment",
        "OPENAI_API_KEY": "your-openai-key",
        "GROQ_API_KEY": "your-groq-key"
      }
    }
  }
}
````

### Installation for Claude Desktop

#### macOS

```bash
# Copy the configuration
cp mcp_config.json ~/Library/Application\ Support/Claude/

# Update paths in the file
nano ~/Library/Application\ Support/Claude/mcp_config.json
```

#### Linux

```bash
# Create the directory if it doesn't exist
mkdir -p ~/.config/claude-desktop/

# Copy the configuration
cp mcp_config.json ~/.config/claude-desktop/

# Update paths in the file
nano ~/.config/claude-desktop/mcp_config.json
```

#### Windows

```cmd
# Copy the configuration
copy mcp_config.json %APPDATA%\Claude\

# Edit the file with a text editor
notepad %APPDATA%\Claude\mcp_config.json
```

### Installation for Cursor

Cursor supports MCP through similar configurations. Refer to the Cursor documentation for specific configuration paths.

## Available Tools

### LLM Server

The LLM server provides the following tools for file operations:

#### llm\_query

* **Description**: Processes complex queries using LLM capabilities with GPT-4o
* **Parameters**:

  * `query` (string): Natural language query
* **Output**: Response with LLM-based reasoning

#### list\_files

* **Description**: Lists all files in the working directory
* **Parameters**: None
* **Output**: File list with metadata (name, size, modification date)

#### read\_file

* **Description**: Reads the content of a file
* **Parameters**:

  * `filename` (string): Name of the file to read
* **Output**: File content as text

#### write\_file

* **Description**: Writes content to a file
* **Parameters**:

  * `filename` (string): Name of the file
  * `content` (string): Content to write
  * `mode` (string, optional): "w" to overwrite, "a" to append
* **Output**: Operation confirmation

#### delete\_file

* **Description**: Deletes a file
* **Parameters**:

  * `filename` (string): Name of the file to delete
* **Output**: Deletion confirmation

## Usage Examples

### Basic Operations in Claude Desktop

**User**: "List all files in the directory"

**Claude**: Will use the `list_files` tool and display:

```
Files in the directory:

document.txt (1.2 KB)
data.json (856 bytes)
script.py (2.1 KB)
image.png (45.3 KB)
```

**User**: "Read the content of document.txt"

**Claude**: Will use the `read_file` tool with parameter `filename: "document.txt"`

### Advanced Operations with LLM Server

**User**: "Find all Python files and summarize what they do"

**Claude with LLM Server**:

1. Uses `list_files` to find .py files
2. Uses `read_file` for each Python file
3. Uses `llm_query` to analyze and summarize the code

**User**: "Create a backup of all important files"

**Claude with LLM Server**:

1. Uses `llm_query` to identify "important" files
2. Uses `read_file` to read contents
3. Uses `write_file` to create backups

## Security and Limitations

### Security Controls

1. **Directory Constraint**: All tools operate only within the specified directory
2. **Path Traversal Protection**: Prevents access to files outside the base directory
3. **Input Validation**: Validates all input parameters
4. **Error Handling**: Secure error handling with no exposure of sensitive information

### Limitations

1. **Limited Scope**: Only file operations in the specified directory
2. **File Size**: Limitations on the size of files that can be processed
3. **File Type**: Optimal support for text files
4. **Concurrency**: Operations are sequential, not parallel

## Troubleshooting

### Server Not Starting

**Issue**: "Server disconnected" in Claude Desktop

**Solutions**:

1. Check paths in the configuration file
2. Verify the virtual environment is correct
3. Check permissions of the working directory
4. Check logs: `/tmp/mcp_server.log`

### API Authentication Errors

**Issue**: Errors with API keys in the LLM server

**Solutions**:

1. Ensure API keys are correctly configured
2. Check the validity of the keys
3. Check environment variable permissions

### Tools Not Working

**Issue**: Tools are unresponsive or return errors

**Solutions**:

1. Test tools manually:

   ```bash
   python -c "
   from agent.tool_registry import ToolRegistry
   registry = ToolRegistry('test_files')
   print(registry.execute_tool('list_files'))
   "
   ```
2. Check directory permissions
3. Inspect logs for specific errors

### Slow Performance

**Issue**: Slow responses from the MCP server

**Solutions**:

1. Use direct queries for simple operations
2. Optimize the working directory size
3. Check internet connection for LLM APIs

## Monitoring and Logs

### Log Files

* **LLM Server**: `/tmp/llm_mcp_server.log`

### Real-Time Monitoring

```bash
# Monitor LLM server logs
tail -f /tmp/llm_mcp_server.log
```

### Useful Metrics

* Number of processed requests
* Average response time
* Errors by type
* API usage (for LLM server)

## Best Practices

### Configuration

1. **Use absolute paths** in the configuration file
2. **Configure API keys** as environment variables
3. **Test configuration** before production use
4. **Keep backups** of working configurations

### Usage

1. **Start with simple operations** to test the connection
2. **Use appropriate queries** for the requested operation
3. **Monitor logs** to identify issues
4. **Limit the size** of the working directory

### Security

1. **Do not expose sensitive directories** as working directories
2. **Use dedicated directories** for the agent
3. **Monitor file access**
4. **Regularly rotate** API keys

## Development and Extensions

### Adding New Tools

1. Implement the tool in `tools/`
2. Register the tool in `agent/tool_registry.py`
3. Add the tool to the MCP servers
4. Update the documentation

### Server Customization

MCP servers can be customized to:

* Add new tools
* Modify validation logic
* Implement caching
* Add custom metrics

### Testing

```bash
# Test MCP configuration
python -c "
import json
with open('mcp_config.json') as f:
    config = json.load(f)
print('Configuration valid')
"

# Test server startup
timeout 5 python server/llm_mcp_server.py --directory test_files || echo 'Server test completed'
