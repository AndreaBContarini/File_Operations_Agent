# **Machine Learning Technical Assignment: Agent Development, Tooling, and MCP Integration**

## 🎯 **Objective**

Design and implement a **tool-using agent** capable of interacting with a file system, answering user queries about files and their content, and exposing its functionality through an **MCP (Model Context Protocol) server**. This assignment evaluates your ability to structure, implement, test, and deploy agentic systems suitable for production environments and developer workflows.

You can use any Agentic framework you are comfortable with. We suggest Pydantic-AI but feel free to user different ones.

---

## ✅ **Requirements**

### **🧩 Step 1: Agent Design with Tooling Approach**

Build an autonomous agent that performs **CRUD operations** and intelligent file queries using a **tool-based architecture**. The agent must reason through user prompts using an internal planning loop (e.g., ReAct, Reflexion, or similar).

### Constraints

- The agent must operate within a **pre-defined base directory**, set at initialization. No tool should accept directory paths as input.
- All file interactions must remain scoped to this directory.

### Required Capabilities

- `list_files() → list[...]`: list all files in the working directory
- `read_file(filename: str) → str`: return file content
- `write_file(filename: str, content: str, mode: str = 'w')`: create, append, or overwrite content
- `delete_file(filename: str)`: delete a file
- `answer_question_about_files(query: str)`: respond to questions by scanning and synthesizing information from across multiple files in the dataset

The agent should be able to execute multiple tools in a single run if needed. For example, if the user asks to read the file that was modified the latest, the agent should first list files, get info about the creation/update times, then pass the filename to read_file, and then return the content.

---

### **💬 Step 2: Chat Interface**

Provide a local, interactive interface for chatting with the agent. This will be used to test the agent’s functionality.

Acceptable options:

- Terminal CLI
- Streamlit / Gradio web app
- Jupyter Notebook with input/output cells
- Direct REST API calls to a local server

You must demonstrate:

- Back-and-forth conversations
- Proper usage of tools within the agent loop
- Safe fallback behavior (e.g., declining invalid actions)

---

### **🌐 Step 3: MCP Server Deployment**

Expose the agent as an **MCP server** so that it can be integrated into clients such as Claude Desktop (<https://modelcontextprotocol.io/quickstart/user>) or Cursor (<https://docs.cursor.com/context/model-context-protocol>).

You must:

- Set up a working MCP server that wraps your agent
- Provide a sample **MCP config/manifest JSON** that can be used by local clients
- Include usage instructions for MCP with any needed credentials, tokens, or environment variables

---

## 🌟 **Bonus Points**

### ✅ Bonus #1: **Pytest Suite**

Provide *some* test coverage for your agent’s logic.

Recommended test areas:

- Tool functionality (list/read/write/delete)
- Edge cases and error handling
- Failure modes (e.g., unreadable files, permission issues)

Use `pytest` and include a `tests/` directory with coverage of both success and failure paths.

### ✅ Bonus #2: Safe & Aligned Behavior

- Agent should actively **decline** to answer irrelevant, unsafe, or off-topic questions
- Explain *why* it is declining, e.g., "I am designed to assist with file-related tasks only."

### ✅ Bonus #3: Lightweight Model for Prompt Rejection

- Use a different and more lightweight model for the steps in Bonus #2, e.g. if the main Agent is using openai:gpt-4o as model, then the model for assessing whether to reject a prompt or not may use a smaller/faster/cheaper model like groq:llama-3.1-8b-instant

---

## 📦 **Deliverables**

Please submit a zip file or GitHub repo that includes a project like:

```bash
/project-root
├── agent/               # Main agent logic
├── tools/               # Tool implementations (also ok as sub-folder in agent folder)
├── chat_interface/      # CLI, notebook, or UI interface
├── server/              # MCP server implementation (also ok as sub-folder in agent folder)
├── tests/               # Pytest test cases
├── mcp_config.json      # Manifest/config for MCP clients
├── requirements.txt     # Python dependencies (or pyproject.toml with poetry.lock or uv.lock)
└── README.md            # Instructions
```

Some example runs/conversations of the agents would be considered a bonus.
