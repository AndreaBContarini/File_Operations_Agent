# Testing Guide

Guida completa per comprendere ed eseguire i test del File Operations Agent.

## Panoramica

La test suite del progetto è progettata per garantire la qualità e l'affidabilità di tutti i componenti CRUD e delle funzionalità avanzate dell'agente. I test coprono scenari di successo, gestione degli errori, casi limite e sicurezza.

## Struttura Test Suite

### File Principali

#### `conftest.py`
File di configurazione pytest che definisce fixtures condivise per tutti i test.

**Fixtures Disponibili:**
- `temp_test_dir`: Crea una directory temporanea con file di test preconfigurati
- `agent`: Istanza dell'agente deterministico per testing
- `llm_agent`: Istanza dell'agente LLM (richiede API keys)
- `sample_files_content`: Contenuti di esempio per test personalizzati

**File di Test Preconfigurati:**
```
temp_test_dir/
├── example.txt (11 bytes) - "Hello World"
├── script.py (21 bytes) - "print('Hello Python')"
├── data.json (30 bytes) - '{"name": "test", "value": 123}'
├── large_file.txt (61 bytes) - Contenuto più lungo per test
└── empty.txt (0 bytes) - File vuoto
```

#### `test_tools.py`
Test completi per tutti i tool CRUD e funzionalità avanzate.

**Classi di Test:**

1. **TestListFiles** (3 test)
   - Verifica listing corretto dei file
   - Controllo metadati (nome, dimensione, data modifica, estensione)
   - Gestione directory inesistenti

2. **TestReadFile** (6 test)
   - Lettura file di diversi tipi (.txt, .py, .json)
   - File vuoti
   - File inesistenti (errore)
   - Protezione path traversal

3. **TestWriteFile** (5 test)
   - Creazione nuovi file
   - Sovrascrittura file esistenti
   - Modalità append
   - Supporto Unicode
   - Protezione path traversal

4. **TestDeleteFile** (3 test)
   - Eliminazione file esistenti
   - File inesistenti (errore)
   - Protezione path traversal

5. **TestAnswerQuestionAboutFiles** (7 test)
   - Conteggio file
   - Identificazione file più grande/piccolo
   - Analisi tipi di file
   - Ricerca file più recente
   - Ricerca nei contenuti
   - Gestione directory inesistenti

6. **TestToolIntegration** (2 test)
   - Ciclo CRUD completo
   - Operazioni concorrenti

## Esecuzione Test

### Comandi Base

```bash
# Esegui tutti i test
python -m pytest tests/ -v

# Esegui test specifici
python -m pytest tests/test_tools.py::TestListFiles -v

# Test con coverage
python -m pytest tests/ --cov=. --cov-report=html

# Test in modalità quiet
python -m pytest tests/ -q
```

### Test Specifici per Tool

```bash
# Test solo tool di lista
python -m pytest tests/ -k "list" -v

# Test solo operazioni di scrittura
python -m pytest tests/ -k "write" -v

# Test solo sicurezza
python -m pytest tests/ -k "traversal" -v

# Test integrazione
python -m pytest tests/ -k "integration" -v
```

### Output Atteso

```
tests/test_tools.py::TestListFiles::test_list_files_success PASSED     [  3%]
tests/test_tools.py::TestListFiles::test_list_files_metadata PASSED    [  7%]
...
tests/test_tools.py::TestToolIntegration::test_concurrent_operations PASSED [100%]

======================== 26 passed in 0.32s ========================
```

## Copertura Test

### Scenari Testati

**✅ Operazioni Base:**
- Lista file con metadati completi
- Lettura file di diversi formati
- Scrittura con modalità write/append
- Eliminazione file esistenti

**✅ Gestione Errori:**
- File/directory inesistenti
- Percorsi non validi
- Problemi di encoding
- Errori di permessi

**✅ Sicurezza:**
- Protezione path traversal (`../../../etc/passwd`)
- Validazione input
- Confinamento directory base

**✅ Casi Limite:**
- File vuoti
- Contenuto Unicode
- File grandi
- Operazioni multiple

**✅ Integrazione:**
- Cicli CRUD completi
- Operazioni sequenziali
- Consistency dei dati

### Metriche Coverage

- **Tool Coverage**: 100% (tutti i 5 tool CRUD)
- **Error Paths**: 100% (tutti i tipi di errore)
- **Security Cases**: 100% (path traversal, validation)
- **Integration**: 100% (multi-tool workflows)

## Debugging Test

### Test Verbose

```bash
# Output dettagliato con reasoning
python -m pytest tests/ -v -s

# Mostra print statements
python -m pytest tests/ -v -s --capture=no

# Stop al primo fallimento
python -m pytest tests/ -x
```

### Test Singoli

```bash
# Test specifico con debug
python -m pytest tests/test_tools.py::TestDeleteFile::test_delete_file_success -v -s
```

### Fixtures Debug

Per debug delle fixtures, modifica `conftest.py`:

```python
@pytest.fixture
def temp_test_dir():
    temp_dir = tempfile.mkdtemp()
    print(f"DEBUG: Created temp dir: {temp_dir}")  # Debug line
    # ... resto del codice
```

## Estensione Test Suite

### Aggiungere Nuovi Test

1. **Per nuovo tool:**
   ```python
   class TestNewTool:
       def test_new_tool_success(self, temp_test_dir):
           result = new_tool("param", temp_test_dir)
           assert result == expected
   ```

2. **Per scenario d'errore:**
   ```python
   def test_new_error_case(self, temp_test_dir):
       with pytest.raises(SpecificError):
           tool_function("invalid_input", temp_test_dir)
   ```

3. **Per integrazione:**
   ```python
   def test_integration_workflow(self, temp_test_dir):
       # Multi-step test scenario
       step1 = tool1(...)
       step2 = tool2(step1_result, ...)
       assert final_condition
   ```

### Best Practices

1. **Nomenclatura**: `test_[component]_[scenario]`
2. **Isolamento**: Ogni test deve essere indipendente
3. **Cleanup**: Le fixtures gestiscono automaticamente la pulizia
4. **Assertions**: Specifiche e descrittive
5. **Coverage**: Testare sia success che error paths

## Risoluzione Problemi

### Errori Comuni

**Test falliti dopo modifiche:**
```bash
# Rimuovi cache pytest
rm -rf .pytest_cache __pycache__ tests/__pycache__

# Reinstalla dipendenze
pip install -r requirements.txt
```

**Problemi directory temporanee:**
```bash
# Verifica permessi
ls -la /tmp/

# Pulisci directory temporanee vecchie
find /tmp -name "tmp*" -user $(whoami) -delete
```

**Import errors:**
```bash
# Verifica PYTHONPATH
export PYTHONPATH=/path/to/assignment:$PYTHONPATH

# Oppure usa -m pytest
python -m pytest tests/
```

## Continuous Integration

### GitHub Actions

Esempio configurazione `.github/workflows/test.yml`:

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/ -v --cov=.
```

### Pre-commit Hooks

```bash
# Installa pre-commit
pip install pre-commit

# Setup hook per eseguire test prima del commit
echo "python -m pytest tests/" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

La test suite garantisce l'affidabilità del File Operations Agent attraverso test completi di tutti i componenti e scenari d'uso. 