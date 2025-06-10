"""
Tool per eliminare un file.
Opera solo all'interno della directory base specificata.
"""
from pathlib import Path


def delete_file(filename: str, base_directory: str) -> bool:
    """
    Elimina un file dalla directory base.
    
    Args:
        filename: Nome del file da eliminare
        base_directory: Percorso alla directory base di lavoro
        
    Returns:
        True se l'operazione ha successo
        
    Raises:
        FileNotFoundError: Se il file non esiste
        ValueError: Se il file non è valido o fuori dalla directory base
        PermissionError: Se non si hanno permessi per eliminare il file
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
            
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} does not exist")
            
        if not file_path.is_file():
            raise ValueError(f"{filename} is not a file")
            
        # Elimina il file
        file_path.unlink() #comando per eliminare il file
        
        return True
        
    except (FileNotFoundError, ValueError):
        # Re-raise questi errori specifici senza wrapping
        raise
    except PermissionError as e:
        raise PermissionError(f"Insufficient permissions to delete {filename}: {e}")
    except OSError as e:
        raise OSError(f"I/O error while deleting file {filename}: {e}") 