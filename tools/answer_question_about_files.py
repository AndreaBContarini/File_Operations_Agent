"""
Tool intelligente per rispondere a domande sui file usando GPT APIs.
Analizza contenuti e metadati per fornire risposte contestuali e sintesi.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import logging
import json
import openai
from datetime import datetime

logger = logging.getLogger(__name__)

# Configurazione OpenAI (sarà impostata dall'agente)
openai_client = None
_current_api_key = None

def set_openai_client(api_key: str):
    """Configura il client OpenAI con la API key."""
    global openai_client, _current_api_key
    openai_client = openai.OpenAI(api_key=api_key)
    _current_api_key = api_key

def answer_question_about_files(base_directory: str, query: str, api_key: Optional[str] = None) -> str:
    """
    Risponde a domande intelligenti sui file analizzando metadati e contenuti.
    
    Questa funzione:
    1. Raccoglie dati completi sui file (metadati + contenuti leggibili)
    2. Usa GPT-4o per analisi intelligente (se API key disponibile)
    3. Fallback su analisi pattern-based se GPT non disponibile
    
    Args:
        base_directory: Directory da analizzare
        query: Domanda dell'utente (es. "What does script.py do?", "What is the largest file?")
        api_key: OpenAI API key (opzionale, se non fornita usa solo analisi basic)
        
    Returns:
        Risposta alla domanda
    """
    try:
        base_path = Path(base_directory)
        
        if not base_path.exists():
            return f"❌ Directory {base_directory} does not exist"
        
        if not base_path.is_dir():
            return f"❌ {base_directory} is not a directory"
        
        # STEP 1: Raccolta dati completi
        files_data = _collect_comprehensive_file_data(base_path)
        
        if files_data["summary"]["total_files"] == 0:
            return "📭 The directory is empty"
        
        # STEP 2: Analisi intelligente
        if api_key:
            # Setup OpenAI client se necessario
            if api_key != _current_api_key:
                set_openai_client(api_key)
            
            # Analisi avanzata con GPT
            return _get_gpt_analysis(files_data, query)
        else:
            # Analisi basic senza AI
            logger.info("No OpenAI API key provided, using basic pattern analysis")
            return _get_basic_analysis(files_data, query)
            
    except Exception as e:
        logger.error(f"Error in answer_question_about_files: {e}")
        return f"❌ Error analyzing files: {str(e)}"

def _collect_comprehensive_file_data(base_path: Path) -> Dict[str, Any]:
    """
    Raccoglie dati completi sui file: metadati + contenuti leggibili.
    
    Args:
        base_path: Path della directory base
        
    Returns:
        Dict con tutti i dati sui file
    """
    files_data = {
        "directory": str(base_path),
        "scan_time": datetime.now().isoformat(),
        "files": [],
        "summary": {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "readable_files": 0
        }
    }
    
    try:
        all_files = list(base_path.iterdir())
        files_data["summary"]["total_files"] = len([f for f in all_files if f.is_file()])
        
        for file_path in all_files:
            if file_path.is_file():
                file_info = _analyze_single_file(file_path)
                files_data["files"].append(file_info)
                
                # Aggiorna summary
                files_data["summary"]["total_size"] += file_info["size"]
                ext = file_info["extension"] or "no_extension"
                files_data["summary"]["file_types"][ext] = files_data["summary"]["file_types"].get(ext, 0) + 1
                
                if file_info["content"]:
                    files_data["summary"]["readable_files"] += 1
    
    except Exception as e:
        logger.error(f"Error collecting file data: {e}")
    
    return files_data

def _analyze_single_file(file_path: Path) -> Dict[str, Any]:
    """
    Analizza un singolo file raccogliendo metadati e contenuto.
    
    Args:
        file_path: Path del file da analizzare
        
    Returns:
        Dict con informazioni complete sul file
    """
    stat = file_path.stat()
    
    file_info = {
        "name": file_path.name,
        "size": stat.st_size,
        "size_formatted": _format_file_size(stat.st_size),
        "modified": stat.st_mtime,
        "modified_formatted": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "extension": file_path.suffix.lower(),
        "content": None,
        "content_preview": None,
        "is_readable": False
    }
    
    # Prova a leggere il contenuto se è un file di testo
    readable_extensions = {'.txt', '.py', '.js', '.json', '.md', '.csv', '.xml', '.yaml', '.yml', 
                          '.ini', '.cfg', '.log', '.sql', '.html', '.css', '.env'}
    
    if file_info["extension"] in readable_extensions or file_info["size"] < 1024 * 1024:  # < 1MB
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            file_info["content"] = content
            file_info["content_preview"] = content[:500] + "..." if len(content) > 500 else content
            file_info["is_readable"] = True
            file_info["lines_count"] = len(content.splitlines())
            file_info["words_count"] = len(content.split())
        except Exception:
            file_info["content"] = None
            file_info["is_readable"] = False
    
    return file_info

def _get_gpt_analysis(files_data: Dict[str, Any], query: str) -> str:
    """
    Usa GPT per analizzare i dati dei file e rispondere alla query.
    
    Args:
        files_data: Dati completi sui file
        query: Domanda dell'utente
        
    Returns:
        Risposta intelligente da GPT
    """
    try:
        # Prepara il context per GPT
        context = _prepare_gpt_context(files_data)
        
        system_prompt = """You are an expert assistant for file and directory analysis.
Analyze the provided file data and respond to user questions intelligently and in detail.

You can:
- Summarize file contents
- Identify patterns and relationships
- Provide detailed statistics
- Analyze code and structures
- Make data inferences
- Suggest improvements

Always respond in English, be precise and provide concrete examples when possible."""

        user_prompt = f"""File data in directory:
{context}

User question: {query}

Analyze the data and provide a complete and useful response."""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error in GPT analysis: {e}")
        return f"❌ Error getting intelligent analysis: {str(e)}"

def _prepare_gpt_context(files_data: Dict[str, Any]) -> str:
    """
    Prepara il context per GPT in formato leggibile.
    
    Args:
        files_data: Dati sui file
        
    Returns:
        Context formattato per GPT
    """
    context_parts = []
    
    # Summary generale
    summary = files_data["summary"]
    context_parts.append(f"""RIEPILOGO DIRECTORY:
- Percorso: {files_data['directory']}
- File totali: {summary['total_files']}
- Dimensione totale: {_format_file_size(summary['total_size'])}
- File leggibili: {summary['readable_files']}
- Tipi di file: {', '.join([f'{count} {ext}' for ext, count in summary['file_types'].items()])}
""")
    
    # Dettagli sui file
    context_parts.append("\nDETTAGLI FILE:")
    
    for file_info in files_data["files"]:
        file_detail = f"""
📄 {file_info['name']}
   - Dimensione: {file_info['size_formatted']}
   - Modificato: {file_info['modified_formatted']}
   - Tipo: {file_info['extension'] or 'nessuna estensione'}"""
        
        if file_info["is_readable"] and file_info["content"]:
            file_detail += f"""
   - Righe: {file_info.get('lines_count', 'N/A')}
   - Parole: {file_info.get('words_count', 'N/A')}
   - Anteprima contenuto:
     {file_info['content_preview']}"""
        
        context_parts.append(file_detail)
    
    return "\n".join(context_parts)

def _get_basic_analysis(files_data: Dict[str, Any], query: str) -> str:
    """
    Fallback analysis senza OpenAI - analisi basic ma utile basata su pattern.
    
    Args:
        files_data: Dati sui file raccolti
        query: Query dell'utente
        
    Returns:
        Risposta basic all'analisi
    """
    try:
        summary = files_data["summary"]
        files = files_data["files"]
        query_lower = query.lower()
        
        # Analisi per tipo di domanda
        if "how many" in query_lower or "count" in query_lower:
            return f"I found {summary['total_files']} files in the directory."
        
        elif "largest" in query_lower or "biggest" in query_lower:
            if files:
                largest = max(files, key=lambda f: f["size"])
                return f"The largest file is '{largest['name']}' ({largest['size_formatted']})."
            return "No files found."
        
        elif "smallest" in query_lower:
            if files:
                smallest = min(files, key=lambda f: f["size"])
                return f"The smallest file is '{smallest['name']}' ({smallest['size_formatted']})."
            return "No files found."
        
        elif "types" in query_lower or "extensions" in query_lower:
            types = summary.get("file_types", {})
            if types:
                type_list = [f"{count} {ext} files" for ext, count in types.items()]
                return f"File types found: {', '.join(type_list)}."
            return "No specific file types identified."
        
        elif "recent" in query_lower or "newest" in query_lower:
            if files:
                most_recent = max(files, key=lambda f: f["modified"])
                return f"The most recent file is '{most_recent['name']}' (modified: {most_recent['modified_formatted']})."
            return "No files found."
        
        elif "cosa fa" in query_lower or "what does" in query_lower:
            # Trova il nome del file nella query
            for file_info in files:
                if file_info["name"].lower() in query_lower:
                    if file_info["is_readable"] and file_info["content"]:
                        return f"File '{file_info['name']}' contains:\n{file_info['content_preview']}"
                    else:
                        return f"File '{file_info['name']}' is a {file_info['extension']} file ({file_info['size_formatted']}) but content cannot be analyzed without AI."
            return "File not found or content cannot be analyzed without AI."
        
        else:
            # Risposta generica informativa
            readable_count = sum(1 for f in files if f["is_readable"])
            return f"""Directory analysis summary:
- Total files: {summary['total_files']}
- Total size: {_format_file_size(summary['total_size'])}
- Readable files: {readable_count}
- File types: {', '.join(summary.get('file_types', {}).keys())}

For detailed analysis of file contents and patterns, OpenAI API integration is required."""
    
    except Exception as e:
        logger.error(f"Error in basic analysis: {e}")
        return f"❌ Error in basic analysis: {str(e)}"

def _format_file_size(size_bytes: int) -> str:
    """
    Formatta la dimensione del file in formato human-readable.
    
    Args:
        size_bytes: Dimensione in bytes
        
    Returns:
        Stringa formattata (es. "1.2 KB", "3.4 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"