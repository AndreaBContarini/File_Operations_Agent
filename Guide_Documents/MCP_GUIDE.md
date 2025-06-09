# Guida MCP (Model Context Protocol)

Guida completa per l'integrazione del File Operations Agent con client MCP come Claude Desktop e Cursor.

## Panoramica MCP

Il Model Context Protocol (MCP) è uno standard aperto che permette agli assistenti AI di connettersi in modo sicuro a fonti di dati e tool esterni. Il nostro File Operations Agent espone le sue funzionalità attraverso un server MCP:

- **Server LLM** (`llm_mcp_server.py`): Operazioni avanzate con capacità di ragionamento LLM e GPT-4o

## Architettura MCP

```
Client MCP (Claude Desktop/Cursor)
    ↓ JSON-RPC 2.0
MCP Server (File Operations Agent)
    ↓ Tool Registry
Tool Implementation (CRUD Operations)
    ↓ File System
Working Directory
```

## Configurazione

### File di Configurazione

Il file `mcp_config.json` definisce i server MCP disponibili:

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
```

### Installazione per Claude Desktop

#### macOS
```bash
# Copia la configurazione
cp mcp_config.json ~/Library/Application\ Support/Claude/

# Aggiorna i percorsi nel file
nano ~/Library/Application\ Support/Claude/mcp_config.json
```

#### Linux
```bash
# Crea la directory se non esiste
mkdir -p ~/.config/claude-desktop/

# Copia la configurazione
cp mcp_config.json ~/.config/claude-desktop/

# Aggiorna i percorsi nel file
nano ~/.config/claude-desktop/mcp_config.json
```

#### Windows
```cmd
# Copia la configurazione
copy mcp_config.json %APPDATA%\Claude\

# Modifica il file con un editor di testo
notepad %APPDATA%\Claude\mcp_config.json
```

### Installazione per Cursor

Cursor supporta MCP attraverso configurazioni simili. Consulta la documentazione di Cursor per i percorsi specifici della configurazione.

## Tool Disponibili

### Server LLM

Il server LLM offre i seguenti tool per operazioni sui file:

#### llm_query
- **Descrizione**: Elabora query complesse usando capacità LLM con GPT-4o
- **Parametri**:
  - `query` (string): Query in linguaggio naturale
- **Output**: Risposta elaborata con ragionamento LLM

#### list_files
- **Descrizione**: Lista tutti i file nella directory di lavoro
- **Parametri**: Nessuno
- **Output**: Lista di file con metadati (nome, dimensione, data modifica)

#### read_file
- **Descrizione**: Legge il contenuto di un file
- **Parametri**: 
  - `filename` (string): Nome del file da leggere
- **Output**: Contenuto del file come testo

#### write_file
- **Descrizione**: Scrive contenuto in un file
- **Parametri**:
  - `filename` (string): Nome del file
  - `content` (string): Contenuto da scrivere
  - `mode` (string, opzionale): "w" per sovrascrivere, "a" per appendere
- **Output**: Conferma dell'operazione

#### delete_file
- **Descrizione**: Elimina un file
- **Parametri**:
  - `filename` (string): Nome del file da eliminare
- **Output**: Conferma dell'eliminazione

## Esempi di Utilizzo

### Operazioni Base in Claude Desktop

**Utente**: "List all files in the directory"

**Claude**: Utilizzerà il tool `list_files` e mostrerà:
```
Files in the directory:

document.txt (1.2 KB)
data.json (856 bytes)
script.py (2.1 KB)
image.png (45.3 KB)
```

**Utente**: "Read the content of document.txt"

**Claude**: Utilizzerà il tool `read_file` con parametro `filename: "document.txt"`

### Operazioni Avanzate con Server LLM

**Utente**: "Find all Python files and summarize what they do"

**Claude con Server LLM**: 
1. Usa `list_files` per trovare file .py
2. Usa `read_file` per ogni file Python
3. Usa `llm_query` per analizzare e riassumere il codice

**Utente**: "Create a backup of all important files"

**Claude con Server LLM**:
1. Usa `llm_query` per identificare file "importanti"
2. Usa `read_file` per leggere i contenuti
3. Usa `write_file` per creare i backup

## Sicurezza e Limitazioni

### Controlli di Sicurezza

1. **Directory Constraint**: Tutti i tool operano solo nella directory specificata
2. **Path Traversal Protection**: Prevenzione di accesso a file fuori dalla directory base
3. **Input Validation**: Validazione di tutti i parametri di input
4. **Error Handling**: Gestione sicura degli errori senza esposizione di informazioni sensibili

### Limitazioni

1. **Scope Limitato**: Solo operazioni sui file nella directory specificata
2. **Dimensione File**: Limitazioni sulla dimensione dei file processabili
3. **Tipo File**: Supporto ottimale per file di testo
4. **Concorrenza**: Operazioni sequenziali, non parallele

## Troubleshooting

### Server Non Si Avvia

**Problema**: "Server disconnected" in Claude Desktop

**Soluzioni**:
1. Verifica i percorsi nel file di configurazione
2. Controlla che il virtual environment sia corretto
3. Verifica i permessi della directory di lavoro
4. Controlla i log: `/tmp/mcp_server.log`

### Errori di Autenticazione API

**Problema**: Errori con le API keys nel server LLM

**Soluzioni**:
1. Verifica che le API keys siano configurate correttamente
2. Controlla la validità delle chiavi
3. Verifica i permessi delle variabili d'ambiente

### Tool Non Funzionano

**Problema**: I tool non rispondono o danno errori

**Soluzioni**:
1. Testa i tool manualmente:
   ```bash
   python -c "
   from agent.tool_registry import ToolRegistry
   registry = ToolRegistry('test_files')
   print(registry.execute_tool('list_files'))
   "
   ```
2. Verifica i permessi della directory
3. Controlla i log per errori specifici

### Performance Lente

**Problema**: Risposte lente dal server MCP

**Soluzioni**:
1. Usa query dirette per operazioni semplici
2. Ottimizza la dimensione della directory di lavoro
3. Verifica la connessione internet per le API LLM

## Monitoraggio e Log

### File di Log

- **Server LLM**: `/tmp/llm_mcp_server.log`

### Monitoraggio in Tempo Reale

```bash
# Monitora log del server LLM
tail -f /tmp/llm_mcp_server.log
```

### Metriche Utili

- Numero di richieste processate
- Tempo di risposta medio
- Errori per tipo
- Utilizzo delle API (per server LLM)

## Best Practices

### Configurazione

1. **Usa percorsi assoluti** nel file di configurazione
2. **Configura API keys** come variabili d'ambiente
3. **Testa la configurazione** prima dell'uso in produzione
4. **Mantieni backup** della configurazione funzionante

### Utilizzo

1. **Inizia con operazioni semplici** per testare la connessione
2. **Usa query appropriate** per il tipo di operazione richiesta
3. **Monitora i log** per identificare problemi
4. **Limita la dimensione** della directory di lavoro

### Sicurezza

1. **Non esporre directory sensibili** come directory di lavoro
2. **Usa directory dedicate** per l'agente
3. **Monitora l'accesso** ai file
4. **Aggiorna regolarmente** le API keys

## Sviluppo e Estensioni

### Aggiungere Nuovi Tool

1. Implementa il tool in `tools/`
2. Registra il tool in `agent/tool_registry.py`
3. Aggiungi il tool ai server MCP
4. Aggiorna la documentazione

### Personalizzazione Server

I server MCP possono essere personalizzati per:
- Aggiungere nuovi tool
- Modificare la logica di validazione
- Implementare caching
- Aggiungere metriche personalizzate

### Testing

```bash
# Test configurazione MCP
python -c "
import json
with open('mcp_config.json') as f:
    config = json.load(f)
print('Configuration valid')
"

# Test server startup
timeout 5 python server/llm_mcp_server.py --directory test_files || echo 'Server test completed'
```

Questa guida fornisce una base completa per l'utilizzo e la configurazione del File Operations Agent tramite MCP.