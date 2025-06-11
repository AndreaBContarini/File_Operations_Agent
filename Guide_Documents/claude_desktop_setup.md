# Setting up Claude Desktop with File Operations Agent

Detailed guide for configuring and using the File Operations Agent with Claude Desktop through MCP.

## Prerequisites

- Claude Desktop installed
- Python 3.8+ with virtual environment configured
- File Operations Agent installed and working
- API keys configured (OpenAI and Groq)

## Step-by-Step Configuration

### 1. Environment Preparation

```bash
# Make sure the virtual environment is active
source .venv/bin/activate

# Verify all dependencies are installed
pip install -r requirements.txt

# Quick system test
python -c "from agent.tool_registry import ToolRegistry; print('System ready')"
```

### 2. MCP Configuration

#### Find the Configuration Directory

**macOS:**
```bash
CONFIG_DIR="$HOME/Library/Application Support/Claude"
```

**Linux:**
```bash
CONFIG_DIR="$HOME/.config/claude-desktop"
```

**Windows:**
```cmd
set CONFIG_DIR=%APPDATA%\Claude
```

#### Create the Configuration

```bash
# Create the directory if it doesn't exist (Linux)
mkdir -p "$CONFIG_DIR"

# Copy the configuration template
cp mcp_config.json "$CONFIG_DIR/"
```

### 3. Configuration Customization

Edit the `mcp_config.json` file in Claude's configuration directory:

```json
{
  "mcpServers": {

    "llm-file-operations-agent": {
      "command": "/ABSOLUTE/PATH/TO/YOUR/.venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/YOUR/assignment/server/llm_mcp_server.py",
        "--directory",
        "/PATH/TO/YOUR/WORK/DIRECTORY",
        "--name",
        "llm-file-operations-agent"
      ],
      "env": {
        "PYTHONPATH": "/ABSOLUTE/PATH/TO/YOUR/assignment",
        "OPENAI_API_KEY": "YOUR_OPENAI_KEY",
        "GROQ_API_KEY": "YOUR_GROQ_KEY"
      }
    }
  }
}
```

### 4. Path Substitution

Use these commands to get the correct paths:

```bash
# Path to virtual environment Python
which python

# Absolute path to the project
pwd

# Path to the work directory (example)
echo "$HOME/Documents/agent_workspace"
```

### 5. Configuration Testing

Before restarting Claude Desktop, test the servers:

```bash
# Test LLM server
python server/llm_mcp_server.py --directory test_files --test
```

### 6. Claude Desktop Restart

1. Completely close Claude Desktop
2. Restart the application
3. Verify that MCP servers are connected

## Installation Verification

### Server Status Check

In Claude Desktop, MCP servers should appear as connected. If you see errors:

1. Check the logs:
   ```bash
   tail -f /tmp/llm_mcp_server.log
   tail -f /tmp/llm_mcp_server.log
   ```

2. Verify the configuration:
   ```bash
   python -c "
   import json
   with open('$CONFIG_DIR/mcp_config.json') as f:
       config = json.load(f)
   print('Configuration loaded successfully')
   "
   ```

### Functionality Testing

Try these commands in Claude Desktop:

**Basic Test:**
```
List all files in the directory
```

**Read Test:**
```
Read the content of example.txt
```

**Write Test:**
```
Create a file called test.txt with the content "Hello from Claude Desktop"
```

**Analysis Test:**
```
What types of files are in the directory and how many of each?
```

## Advanced Usage

### Multi-Step Operations

Claude Desktop can orchestrate complex operations:

```
Find all Python files, read their content, and create a summary document
```

This command will:
1. List files to find .py ones
2. Read the content of each Python file
3. Analyze the code
4. Create a summary document

### Backup and File Management

```
Create backups of all important files by copying them with a timestamp suffix
```

### Content Analysis

```
Analyze all text files and tell me which ones contain specific keywords
```

## Troubleshooting

### Disconnected Server

**Symptoms:** "Server disconnected" in Claude Desktop

**Solutions:**
1. Verify paths in the configuration file
2. Check that the virtual environment is correct
3. Verify directory permissions
4. Check logs for specific errors

### Permission Errors

**Symptoms:** File access errors

**Solutions:**
```bash
# Check work directory permissions
ls -la /path/to/work/directory

# Fix permissions if necessary
chmod 755 /path/to/work/directory
chmod 644 /path/to/work/directory/*
```

### Non-Working API Keys

**Symptoms:** Errors with the LLM server

**Solutions:**
1. Verify that API keys are valid
2. Check usage limits
3. Test keys manually:
   ```bash
   python -c "
   import os
   from openai import OpenAI
   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
   print('OpenAI key works')
   "
   ```

### Slow Performance

**Symptoms:** Slow responses from Claude Desktop

**Solutions:**
1. Use the LLM server with direct queries for simple operations
2. Reduce the size of the work directory
3. Check internet connection

## Advanced Configurations

### Multiple Directories

You can configure servers for different directories:

```json
{
  "mcpServers": {
    "documents-agent": {
      "command": "/path/to/.venv/bin/python",
      "args": [
        "/path/to/assignment/server/mcp_server.py",
        "--directory",
        "/path/to/documents",
        "--name",
        "documents-agent"
      ]
    },
    "projects-agent": {
      "command": "/path/to/.venv/bin/python",
      "args": [
        "/path/to/assignment/server/mcp_server.py",
        "--directory",
        "/path/to/projects",
        "--name",
        "projects-agent"
      ]
    }
  }
}
```

### Secure Configuration

For production environments:

```json
{
  "mcpServers": {
    "secure-file-agent": {
      "command": "/path/to/.venv/bin/python",
      "args": [
        "/path/to/assignment/server/mcp_server.py",
        "--directory",
        "/secure/sandbox/directory",
        "--name",
        "secure-file-agent",
        "--readonly"
      ],
      "env": {
        "PYTHONPATH": "/path/to/assignment",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Best Practices

### Security

1. **Use dedicated directories** for the agent, not system directories
2. **Limit permissions** of the work directory
3. **Don't expose sensitive directories** like home or root
4. **Monitor activity** through logs

### Performance

1. **Keep directories small** for better performance
2. **Use the appropriate server** (deterministic vs LLM)
3. **Regularly clean** temporary files
4. **Monitor API usage** to control costs

### Maintenance

1. **Regularly update** API keys
2. **Monitor logs** to identify issues
3. **Test configuration** after changes
4. **Keep backups** of working configuration

## Support

For unresolved issues:

1. Check detailed logs
2. Verify configuration with test scripts
3. Consult official MCP documentation
4. Contact technical support

This configuration will allow you to use the File Operations Agent directly in Claude Desktop with all its advanced features.
