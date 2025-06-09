"""
Tool per elencare tutti i file nella directory di lavoro.
Opera solo all'interno della directory base specificata.
"""

import os #non usato direttamente
from pathlib import Path # pathlib.Path: classe moderna che ho trovato, per gestire percorsi di file in modo + leggibile rispetto a os.path.
from typing import List, Dict, Any


def list_files(base_directory: str) -> List[Dict[str, Any]]:
    """
    Lista tutti i file nella directory base con metadati dettagliati.
    
    Args:
        base_directory: Percorso alla directory base di lavoro
        
    Returns:
        Lista di dizionari con informazioni sui file (nome, dimensione, data modifica)
        
    Raises:
        ValueError: Se la directory base non esiste
    """
    try:
        base_path = Path(base_directory)
        
        if not base_path.exists():
            raise ValueError(f"Base directory {base_directory} does not exist")
            
        if not base_path.is_dir():
            raise ValueError(f"{base_directory} is not a directory")
        
        files_info = []
        
        for file_path in base_path.iterdir():
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    files_info.append({
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "extension": file_path.suffix.lower() if file_path.suffix else "",
                        "is_directory": False
                    })
                except (PermissionError, OSError):
                    # Salta file inaccessibili
                    continue
        
        # Ordina per nome
        files_info.sort(key=lambda x: x["name"])
        
        return files_info
        
    except Exception as e:
        raise Exception(f"Error while listing files: {e}") 