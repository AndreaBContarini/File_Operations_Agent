# Environment Configuration

Complete guide for configuring the development and production environment for the File Operations Agent.

## System Prerequisites

### Python
- **Required version**: Python 3.8 or higher
- **Recommended version**: Python 3.10+

Check the installed version:
```bash
python --version
# or
python3 --version
```

### Virtual Environment
Strongly recommended to isolate dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Verify activation
which python  # should point to .venv/bin/python
```

## Dependencies Installation

### Core Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install manually:
pip install openai groq pathlib typing-extensions pytest
```

### Development Dependencies
```bash
# For development and testing
pip install pytest pytest-cov black flake8 mypy
```

## API Keys Configuration

### Method 1: .env File (Recommended)

Create a `.env` file in the project root:

```env
# OpenAI API Key for GPT-4o
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Groq API Key for LLaMA 3 8B
GROQ_API_KEY=gsk_your-groq-key-here

# Optional: Additional configurations
PYTHONPATH=/path/to/assignment
LOG_LEVEL=INFO
```

### Method 2: Environment Variables

```bash
# Export temporarily (current session)
export OPENAI_API_KEY="sk-proj-your-openai-key-here"
export GROQ_API_KEY="gsk_your-groq-key-here"

# Add to shell profile for persistence
echo 'export OPENAI_API_KEY="sk-proj-your-openai-key-here"' >> ~/.bashrc
echo 'export GROQ_API_KEY="gsk_your-groq-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Method 3: Direct Configuration in Code

**Not recommended for production**

```python
import os
os.environ['OPENAI_API_KEY'] = 'your-key-here'
os.environ['GROQ_API_KEY'] = 'your-key-here'
```

## Obtaining API Keys

### OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account or log in
3. Navigate to "API Keys" in the dashboard
4. Click "Create new secret key"
5. Copy the key (starts with `sk-proj-`)

### Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Create an account or log in
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Copy the key (starts with `gsk_`)

## Work Directory Configuration

### Recommended Structure

```
/your-workspace/
├── assignment/           # Project code
│   ├── .venv/           # Virtual environment
│   ├── .env             # API keys
│   └── ...
└── work_directory/      # Work directory for files
    ├── documents/
    ├── data/
    └── temp/
```

### Directory Permissions

```bash
# Ensure work directory has correct permissions
chmod 755 /path/to/work_directory
chmod 644 /path/to/work_directory/*

# For temporary directories
mkdir -p /tmp/agent_work
chmod 777 /tmp/agent_work
```

## MCP Configuration

### Claude Desktop

1. **Find the configuration directory:**
   - macOS: `~/Library/Application Support/Claude/`
   - Linux: `~/.config/claude-desktop/`
   - Windows: `%APPDATA%\Claude\`

2. **Copy the configuration:**
   ```bash
   # macOS
   cp mcp_config.json ~/Library/Application\ Support/Claude/

   # Linux
   cp mcp_config.json ~/.config/claude-desktop/

   # Windows
   copy mcp_config.json %APPDATA%\Claude\
   ```

3. **Update paths in the file:**
   ```json
   {
     "mcpServers": {
       "file-operations-agent": {
         "command": "/path/to/your/.venv/bin/python",
         "args": [
           "/path/to/your/assignment/server/llm_mcp_server.py",
           "--directory",
           "/path/to/your/work_directory"
         ]
       }
     }
   }
   ```

### Cursor IDE

For Cursor, MCP configuration is similar but may require different paths. Consult Cursor's documentation for specific details.

## Configuration Verification

### Basic Test

```bash
# Test dependency imports
python -c "import openai, groq; print('Dependencies OK')"

# Test API keys
python -c "
import os
assert os.getenv('OPENAI_API_KEY'), 'OpenAI key missing'
assert os.getenv('GROQ_API_KEY'), 'Groq key missing'
print('API keys configured')
"
```

### Functionality Test

```bash
# Test CLI
python chat_interface/cli.py --directory test_files --test

# Test tool registry
python -c "
from agent.tool_registry import ToolRegistry
registry = ToolRegistry('test_files')
print('Available tools:', list(registry.list_tools().keys()))
"
```

### MCP Server Test

```bash
# Test server startup
python server/llm_mcp_server.py --directory test_files --test

# Test with simulated input
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | \
python server/llm_mcp_server.py --directory test_files
```

## Troubleshooting

### Common Issues

#### Import Error
```
ModuleNotFoundError: No module named 'openai'
```
**Solution:**
```bash
# Verify virtual environment is active
which python
pip install -r requirements.txt
```

#### API Key Error
```
openai.AuthenticationError: Incorrect API key provided
```
**Solution:**
```bash
# Verify configuration
echo $OPENAI_API_KEY
# Regenerate key if necessary
```

#### Permission Error
```
PermissionError: [Errno 13] Permission denied
```
**Solution:**
```bash
# Fix directory permissions
chmod 755 /path/to/directory
# Verify ownership
ls -la /path/to/directory
```

#### MCP Connection Error
```
Server disconnected
```
**Solution:**
1. Verify paths in configuration file
2. Check server log: `/tmp/llm_mcp_server.log`
3. Test server manually

### Logging and Debug

#### Enable Detailed Logging

```bash
# Environment variable for debug
export LOG_LEVEL=DEBUG

# Custom log file
export LOG_FILE=/tmp/agent_debug.log
```

#### MCP Log Monitoring

```bash
# Monitor log in real time
tail -f /tmp/llm_mcp_server.log
```

## Production Configuration

### Security

1. **Don't commit API keys to repository**
2. **Use .env file with restrictive permissions:**
   ```bash
   chmod 600 .env
   ```
3. **Consider using secret management tools**

### Performance

1. **Configure appropriate timeouts**
2. **Limit processable file sizes**
3. **Implement rate limiting for API calls**

### Monitoring

1. **Configure structured logging**
2. **Implement health checks**
3. **Monitor API usage**

## Advanced Configurations

### Proxy Configuration

If behind a corporate proxy:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1
```

### Custom Model Configuration

To use different models:

```python
# In agent/llm_validator.py
GROQ_MODEL = "llama-3.1-70b-versatile"  # More powerful model
OPENAI_MODEL = "gpt-4o-mini"            # More economical model
```

### Batch Processing

For large volume processing:

```python
# Batch configuration
BATCH_SIZE = 100
MAX_CONCURRENT_REQUESTS = 5
REQUEST_TIMEOUT = 30
```
