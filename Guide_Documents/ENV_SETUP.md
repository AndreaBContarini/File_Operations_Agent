# Configurazione Ambiente

Guida completa per la configurazione dell'ambiente di sviluppo e produzione per il File Operations Agent.

## Prerequisiti di Sistema

### Python
- **Versione richiesta**: Python 3.8 o superiore
- **Versione raccomandata**: Python 3.10+

Verifica la versione installata:
```bash
python --version
# oppure
python3 --version
```

### Virtual Environment
Fortemente raccomandato per isolare le dipendenze:

```bash
# Crea virtual environment
python -m venv .venv

# Attiva virtual environment
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Verifica attivazione
which python  # dovrebbe puntare a .venv/bin/python
```

## Installazione Dipendenze

### Dipendenze Core
```bash
# Installa tutte le dipendenze
pip install -r requirements.txt

# Oppure installa manualmente:
pip install openai groq pathlib typing-extensions pytest
```

### Dipendenze di Sviluppo
```bash
# Per sviluppo e testing
pip install pytest pytest-cov black flake8 mypy
```

## Configurazione API Keys

### Metodo 1: File .env (Raccomandato)

Crea un file `.env` nella root del progetto:

```env
# OpenAI API Key per GPT-4o
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Groq API Key per LLaMA 3 8B
GROQ_API_KEY=gsk_your-groq-key-here

# Opzionale: Configurazioni aggiuntive
PYTHONPATH=/path/to/assignment
LOG_LEVEL=INFO
```

### Metodo 2: Variabili d'Ambiente

```bash
# Esporta temporaneamente (sessione corrente)
export OPENAI_API_KEY="sk-proj-your-openai-key-here"
export GROQ_API_KEY="gsk_your-groq-key-here"

# Aggiungi al profilo shell per persistenza
echo 'export OPENAI_API_KEY="sk-proj-your-openai-key-here"' >> ~/.bashrc
echo 'export GROQ_API_KEY="gsk_your-groq-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Metodo 3: Configurazione Diretta nel Codice

**Non raccomandato per produzione**

```python
import os
os.environ['OPENAI_API_KEY'] = 'your-key-here'
os.environ['GROQ_API_KEY'] = 'your-key-here'
```

## Ottenere le API Keys

### OpenAI API Key

1. Vai su [platform.openai.com](https://platform.openai.com)
2. Crea un account o effettua il login
3. Naviga su "API Keys" nel dashboard
4. Clicca "Create new secret key"
5. Copia la chiave (inizia con `sk-proj-`)

### Groq API Key

1. Vai su [console.groq.com](https://console.groq.com)
2. Crea un account o effettua il login
3. Naviga su "API Keys"
4. Clicca "Create API Key"
5. Copia la chiave (inizia con `gsk_`)

## Configurazione Directory di Lavoro

### Struttura Raccomandata

```
/your-workspace/
├── assignment/           # Codice del progetto
│   ├── .venv/           # Virtual environment
│   ├── .env             # API keys
│   └── ...
└── work_directory/      # Directory di lavoro per i file
    ├── documents/
    ├── data/
    └── temp/
```

### Permessi Directory

```bash
# Assicurati che la directory di lavoro abbia i permessi corretti
chmod 755 /path/to/work_directory
chmod 644 /path/to/work_directory/*

# Per directory temporanee
mkdir -p /tmp/agent_work
chmod 777 /tmp/agent_work
```

## Configurazione MCP

### Claude Desktop

1. **Trova la directory di configurazione:**
   - macOS: `~/Library/Application Support/Claude/`
   - Linux: `~/.config/claude-desktop/`
   - Windows: `%APPDATA%\Claude\`

2. **Copia la configurazione:**
   ```bash
   # macOS
   cp mcp_config.json ~/Library/Application\ Support/Claude/

   # Linux
   cp mcp_config.json ~/.config/claude-desktop/

   # Windows
   copy mcp_config.json %APPDATA%\Claude\
   ```

3. **Aggiorna i percorsi nel file:**
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

Per Cursor, la configurazione MCP è simile ma potrebbe richiedere percorsi diversi. Consulta la documentazione di Cursor per dettagli specifici.

## Verifica Configurazione

### Test Base

```bash
# Test import delle dipendenze
python -c "import openai, groq; print('Dependencies OK')"

# Test API keys
python -c "
import os
assert os.getenv('OPENAI_API_KEY'), 'OpenAI key missing'
assert os.getenv('GROQ_API_KEY'), 'Groq key missing'
print('API keys configured')
"
```

### Test Funzionalità

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

### Test MCP Server

```bash
# Test server startup
python server/llm_mcp_server.py --directory test_files --test

# Test con input simulato
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | \
python server/llm_mcp_server.py --directory test_files
```

## Troubleshooting

### Problemi Comuni

#### Import Error
```
ModuleNotFoundError: No module named 'openai'
```
**Soluzione:**
```bash
# Verifica virtual environment attivo
which python
pip install -r requirements.txt
```

#### API Key Error
```
openai.AuthenticationError: Incorrect API key provided
```
**Soluzione:**
```bash
# Verifica configurazione
echo $OPENAI_API_KEY
# Rigenera la chiave se necessario
```

#### Permission Error
```
PermissionError: [Errno 13] Permission denied
```
**Soluzione:**
```bash
# Correggi permessi directory
chmod 755 /path/to/directory
# Verifica ownership
ls -la /path/to/directory
```

#### MCP Connection Error
```
Server disconnected
```
**Soluzione:**
1. Verifica percorsi nel file di configurazione
2. Controlla log del server: `/tmp/llm_mcp_server.log`
3. Testa il server manualmente

### Log e Debug

#### Abilitare Logging Dettagliato

```bash
# Variabile d'ambiente per debug
export LOG_LEVEL=DEBUG

# Log file personalizzato
export LOG_FILE=/tmp/agent_debug.log
```

#### Monitoraggio Log MCP

```bash
# Monitora log in tempo reale
tail -f /tmp/llm_mcp_server.log
```

## Configurazione Produzione

### Sicurezza

1. **Non committare API keys nel repository**
2. **Usa file .env con permessi restrittivi:**
   ```bash
   chmod 600 .env
   ```
3. **Considera l'uso di secret management tools**

### Performance

1. **Configura timeout appropriati**
2. **Limita dimensioni file processabili**
3. **Implementa rate limiting per API calls**

### Monitoring

1. **Configura logging strutturato**
2. **Implementa health checks**
3. **Monitora usage delle API**

## Configurazioni Avanzate

### Proxy Configuration

Se dietro un proxy aziendale:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1
```

### Custom Model Configuration

Per utilizzare modelli diversi:

```python
# In agent/llm_validator.py
GROQ_MODEL = "llama-3.1-70b-versatile"  # Modello più potente
OPENAI_MODEL = "gpt-4o-mini"            # Modello più economico
```

### Batch Processing

Per elaborazione di grandi volumi:

```python
# Configurazione batch
BATCH_SIZE = 100
MAX_CONCURRENT_REQUESTS = 5
REQUEST_TIMEOUT = 30
```

Questa configurazione garantisce un ambiente robusto e sicuro per il File Operations Agent. 