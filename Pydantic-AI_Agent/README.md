# Agent Pydantic-AI Hybrid

Implementazione ibrida dell'agente per operazioni sui file utilizzando il framework **Pydantic-AI** con architettura dual-model.

## Obiettivo

Questo modulo implementa un sistema ibrido che combina:

- **OpenAI GPT-4o**: Operazioni sui file e reasoning avanzato
- **Groq llama-3.1-8b-instant**: Validazione query e sicurezza (opzionale)
- **Pydantic-AI Framework**: Tool orchestration nativa e structured output

## Architettura

### Componenti Principali

1. **`PydanticFileAgent`** - Agent principale con architettura ibrida
2. **`AgentDependencies`** - Dependency injection type-safe
3. **`AgentResponse`** - Structured output con validazione Pydantic
4. **Dual-Model System** - GPT-4o per operazioni, Groq per validazione

### Flusso di Elaborazione

```
User Query
    ↓
[Optional] Groq Validation (SAFE/DANGEROUS)
    ↓
GPT-4o File Operations (with tools)
    ↓
Structured AgentResponse
```

### Confronto con Implementazioni Precedenti

| Aspetto | Implementazione Originale | Pydantic-AI Hybrid |
|---------|---------------------------|-------------------|
| **Architecture** | Single model custom planner | Dual-model hybrid system |
| **Tool Registry** | Custom ToolRegistry | Native Pydantic-AI tools |
| **Output** | Dict non strutturato | Structured Pydantic models |
| **Validation** | Manual validation | Automatic + security layer |
| **Orchestration** | Manual step-by-step | Declarative + intelligent routing |
| **Security** | Basic input validation | Dedicated validation model |

## Utilizzo

### CLI Interattiva

```bash
cd agent_pydantic
python pydantic_cli.py --create-samples -d ./test_files
```

Il CLI supporta:
- Configurazione API interattiva (OpenAI required, Groq optional)
- Comandi speciali (`/help`, `/status`, `/verbose`, etc.)
- Query in linguaggio naturale
- Modalità verbosa per debugging

### Utilizzo Programmatico

```python
import asyncio
from pydantic_agent import PydanticFileAgent

async def main():
    # Inizializza l'agent ibrido
    agent = PydanticFileAgent(
        base_directory="/path/to/files",
        openai_api_key="sk-...",
        groq_api_key="gsk_...",  # Optional
        verbose=True
    )
    
    # Esegui query con structured output
    response = await agent.process_query("List all files and tell me which is the largest")
    
    print(f"Success: {response.success}")
    print(f"Message: {response.message}")
    print(f"Type: {response.type}")
    if response.files:
        print(f"Files found: {len(response.files)}")

asyncio.run(main())
```

## Tool Disponibili

Tutti i tool sono implementati come native Pydantic-AI tools:

- **`list_files_tool()`** - Lista file con metadati completi
- **`read_file_tool(filename, encoding)`** - Legge contenuto file
- **`write_file_tool(filename, content, mode, encoding)`** - Scrive/crea file
- **`delete_file_tool(filename)`** - Elimina file
- **`answer_question_tool(query)`** - Analisi intelligente sui file

### Caratteristiche dei Tool

- **Validazione automatica** dei parametri con Pydantic
- **Error handling** robusto con messaging dettagliato
- **Dependency injection** type-safe
- **Logging** configurabile per debugging

## Structured Output

L'agent restituisce sempre un `AgentResponse` validato:

```python
class AgentResponse(BaseModel):
    success: bool
    message: str
    type: str
    
    # Dati opzionali
    files: Optional[List[Dict[str, Any]]] = None
    file_content: Optional[str] = None
    analysis_result: Optional[str] = None
    operations_performed: Optional[List[str]] = None
    reasoning: Optional[str] = None
```

## Configurazione

### API Keys Required

- **OpenAI API Key**: Required per GPT-4o (operazioni sui file)
- **Groq API Key**: Optional per llama-3.1-8b-instant (validazione)

### Modelli Supportati

#### File Operations (Required)
- **OpenAI GPT-4o**: Modello principale per operazioni sui file

#### Validation (Optional)
- **Groq llama-3.1-8b-instant**: Validazione query per sicurezza

## Sicurezza

### Validation Layer

Se configurato, Groq fornisce un layer di sicurezza che:
- Analizza le query utente prima dell'esecuzione
- Classifica come SAFE o DANGEROUS
- Blocca operazioni potenzialmente pericolose
- Previene path traversal e comandi di sistema

### Fallback Mechanism

- Se Groq non è disponibile: procede direttamente con GPT-4o
- Se Groq fallisce: continua l'elaborazione con logging dell'errore
- Nessuna interruzione del servizio per problemi di validazione

## Testing e Esempi

### CLI Testing

```bash
# Test con file di esempio
python pydantic_cli.py --create-samples -d ./test_files

# Test query comuni
> list all files
> read config.json
> create a file test.txt with content Hello World
> delete old.txt
> analyze all Python files
```

### Query di Esempio

- "List all files in the directory"
- "Read the content of config.json" 
- "Create a file called test.txt with content Hello World"
- "Delete the file old.txt"
- "What is the largest file in the directory?"
- "Analyze all Python files and tell me what they do"

## Multi-Step Reasoning

L'agent GPT-4o gestisce automaticamente task complessi:

```python
# Query complessa automaticamente scomposta
response = await agent.process_query(
    "Count the files, then read the most recent one and summarize it"
)

# L'agent automaticamente:
# 1. Chiama list_files_tool() per contare i file
# 2. Analizza i metadati per trovare il file più recente  
# 3. Chiama read_file_tool() per leggere il contenuto
# 4. Genera un riassunto del contenuto
# 5. Restituisce una risposta strutturata
```

## Vantaggi dell'Architettura Ibrida

### 1. Sicurezza Migliorata
- Validation layer dedicato con Groq
- Prevenzione di operazioni pericolose
- Sanitizzazione automatica delle query

### 2. Performance Ottimizzate
- GPT-4o dedicato alle operazioni sui file
- Modello di validazione lightweight (llama-3.1-8b-instant)
- Routing intelligente delle richieste

### 3. Reliability
- Fallback automatico se validazione non disponibile
- Error handling robusto su entrambi i modelli
- Graceful degradation

### 4. Structured Output
- Output sempre validato con Pydantic
- Schema consistente per tutte le risposte
- Type safety completa

### 5. Developer Experience
- CLI interattiva user-friendly
- Logging configurabile
- Configurazione API semplificata

## File Structure

```
agent_pydantic/
├── pydantic_agent.py      # Agent principale ibrido
├── pydantic_cli.py        # CLI interattiva
├── models.py              # Pydantic models
├── dependencies.py        # Dependency injection
└── README.md              # Questa documentazione
```

## Error Handling

- **Validation errors**: Gestiti dal layer Groq con fallback
- **File operation errors**: Gestiti da GPT-4o con retry automatico
- **Structured error responses**: Sempre validate con Pydantic
- **Detailed logging**: Configurabile per debugging

## Performance

L'implementazione ibrida offre:

- **Reasoning efficiente** con GPT-4o dedicato
- **Validazione veloce** con llama-3.1-8b-instant
- **Memory usage ottimizzato** senza state management custom
- **Latency controllata** con routing intelligente

---

**Note**: Questa implementazione dimostra come un'architettura ibrida possa combinare i punti di forza di diversi modelli LLM, mantenendo sicurezza, performance e usabilità in un sistema di produzione. 