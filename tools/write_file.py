"""
Tool per scrivere contenuto in un file.
Opera solo all'interno della directory base specificata.
"""
from pathlib import Path
from typing import Literal


def write_file(filename: str, content: str, base_directory: str, 
               mode: Literal['w', 'a'] = 'w', 
               encoding: str = 'utf-8') -> bool: # Restituisco bool -- cioè True se l'operazione ha successo, False altrimenti
    """
    Scrive contenuto in un file nella directory base.
    
    Args:
        filename: Nome del file da scrivere
        content: Contenuto da scrivere nel file
        base_directory: Percorso alla directory base di lavoro
        mode: Modalità di scrittura ('w' per sovrascrivere, 'a' per appendere)
        encoding: Encoding del file (default: utf-8)
        
    Returns:
        True se l'operazione ha successo
        
    Raises:
        ValueError: Se il percorso del file non è valido
        PermissionError: Se non si hanno permessi per scrivere il file
        OSError: Se si verifica un errore di I/O
    """
    try:
        base_path = Path(base_directory)
        file_path = base_path / filename
        
        # Verifica che il file sia all'interno della directory base
        try:
            file_path.resolve().relative_to(base_path.resolve())
        except ValueError:
            raise ValueError(f"File {filename} is not within the base directory")
            
        # Verifica che la directory base esista
        if not base_path.exists():
            raise ValueError(f"Base directory {base_directory} does not exist")
            
        # Crea le sottodirectory se necessario
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Scrive il file
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content) # scrive il contenuto nel file
            
        return True # ritorna True se l'operazione ha successo
        
    except PermissionError as e:
        raise PermissionError(f"Insufficient permissions to write {filename}: {e}")
    except OSError as e:
        raise OSError(f"I/O error while writing file {filename}: {e}")
    except Exception as e:
        raise Exception(f"Error while writing file {filename}: {e}") 