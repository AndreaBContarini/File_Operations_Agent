# Setup Claude Desktop con File Operations Agent

Guida dettagliata per configurare e utilizzare il File Operations Agent con Claude Desktop tramite MCP.

## Prerequisiti

- Claude Desktop installato
- Python 3.8+ con virtual environment configurato
- File Operations Agent installato e funzionante
- API keys configurate (OpenAI e Groq)

## Configurazione Passo-Passo

### 1. Preparazione dell'Ambiente

```bash
# Assicurati che il virtual environment sia attivo
source .venv/bin/activate

# Verifica che tutte le dipendenze siano installate
pip install -r requirements.txt

# Test rapido del sistema
python -c "from agent.tool_registry import ToolRegistry; print('System ready')"
```

### 2. Configurazione MCP

#### Trova la Directory di Configurazione

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

#### Crea la Configurazione

```bash
# Crea la directory se non esiste (Linux)
mkdir -p "$CONFIG_DIR"

# Copia il template di configurazione
cp mcp_config.json "$CONFIG_DIR/"
```

### 3. Personalizzazione della Configurazione

Modifica il file `mcp_config.json` nella directory di configurazione di Claude:

```json
{
  "mcpServers": {

    "llm-file-operations-agent": {
      "command": "/PERCORSO/ASSOLUTO/AL/TUO/.venv/bin/python",
      "args": [
        "/PERCORSO/ASSOLUTO/AL/TUO/assignment/server/llm_mcp_server.py",
        "--directory",
        "/PERCORSO/ALLA/TUA/DIRECTORY/DI/LAVORO",
        "--name",
        "llm-file-operations-agent"
      ],
      "env": {
        "PYTHONPATH": "/PERCORSO/ASSOLUTO/AL/TUO/assignment",
        "OPENAI_API_KEY": "LA_TUA_CHIAVE_OPENAI",
        "GROQ_API_KEY": "LA_TUA_CHIAVE_GROQ"
      }
    }
  }
}
```

### 4. Sostituzione dei Percorsi

Usa questi comandi per ottenere i percorsi corretti:

```bash
# Percorso al virtual environment Python
which python

# Percorso assoluto al progetto
pwd

# Percorso alla directory di lavoro (esempio)
echo "$HOME/Documents/agent_workspace"
```

### 5. Test della Configurazione

Prima di riavviare Claude Desktop, testa i server:

```bash
# Test server LLM
python server/llm_mcp_server.py --directory test_files --test
```

### 6. Riavvio di Claude Desktop

1. Chiudi completamente Claude Desktop
2. Riavvia l'applicazione
3. Verifica che i server MCP siano connessi

## Verifica dell'Installazione

### Controllo Stato Server

In Claude Desktop, i server MCP dovrebbero apparire come connessi. Se vedi errori:

1. Controlla i log:
   ```bash
   tail -f /tmp/llm_mcp_server.log
   tail -f /tmp/llm_mcp_server.log
   ```

2. Verifica la configurazione:
   ```bash
   python -c "
   import json
   with open('$CONFIG_DIR/mcp_config.json') as f:
       config = json.load(f)
   print('Configuration loaded successfully')
   "
   ```

### Test Funzionalità

Prova questi comandi in Claude Desktop:

**Test Base:**
```
List all files in the directory
```

**Test Lettura:**
```
Read the content of example.txt
```

**Test Scrittura:**
```
Create a file called test.txt with the content "Hello from Claude Desktop"
```

**Test Analisi:**
```
What types of files are in the directory and how many of each?
```

## Utilizzo Avanzato

### Operazioni Multi-Step

Claude Desktop può orchestrare operazioni complesse:

```
Find all Python files, read their content, and create a summary document
```

Questo comando farà:
1. Lista i file per trovare quelli .py
2. Legge il contenuto di ogni file Python
3. Analizza il codice
4. Crea un documento di riepilogo

### Backup e Gestione File

```
Create backups of all important files by copying them with a timestamp suffix
```

### Analisi Contenuti

```
Analyze all text files and tell me which ones contain specific keywords
```

## Troubleshooting

### Server Disconnesso

**Sintomi:** "Server disconnected" in Claude Desktop

**Soluzioni:**
1. Verifica i percorsi nel file di configurazione
2. Controlla che il virtual environment sia corretto
3. Verifica i permessi della directory
4. Controlla i log per errori specifici

### Errori di Permessi

**Sintomi:** Errori di accesso ai file

**Soluzioni:**
```bash
# Verifica permessi directory di lavoro
ls -la /path/to/work/directory

# Correggi permessi se necessario
chmod 755 /path/to/work/directory
chmod 644 /path/to/work/directory/*
```

### API Keys Non Funzionanti

**Sintomi:** Errori con il server LLM

**Soluzioni:**
1. Verifica che le API keys siano valide
2. Controlla i limiti di utilizzo
3. Testa le chiavi manualmente:
   ```bash
   python -c "
   import os
   from openai import OpenAI
   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
   print('OpenAI key works')
   "
   ```

### Performance Lente

**Sintomi:** Risposte lente da Claude Desktop

**Soluzioni:**
1. Usa il server LLM con query dirette per operazioni semplici
2. Riduci la dimensione della directory di lavoro
3. Verifica la connessione internet

## Configurazioni Avanzate

### Directory Multiple

Puoi configurare server per directory diverse:

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

### Configurazione Sicura

Per ambienti di produzione:

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

### Sicurezza

1. **Usa directory dedicate** per l'agente, non directory di sistema
2. **Limita i permessi** della directory di lavoro
3. **Non esporre directory sensibili** come home o root
4. **Monitora l'attività** attraverso i log

### Performance

1. **Mantieni directory piccole** per performance migliori
2. **Usa il server appropriato** (deterministico vs LLM)
3. **Pulisci regolarmente** i file temporanei
4. **Monitora l'uso delle API** per controllare i costi

### Manutenzione

1. **Aggiorna regolarmente** le API keys
2. **Monitora i log** per identificare problemi
3. **Testa la configurazione** dopo modifiche
4. **Mantieni backup** della configurazione funzionante

## Supporto

Per problemi non risolti:

1. Controlla i log dettagliati
2. Verifica la configurazione con gli script di test
3. Consulta la documentazione MCP ufficiale
4. Contatta il supporto tecnico

Questa configurazione ti permetterà di utilizzare il File Operations Agent direttamente in Claude Desktop con tutte le sue funzionalità avanzate. 