"""
Tool per leggere il contenuto di un file.
Opera solo all'interno della directory base specificata.
"""
from pathlib import Path
import mimetypes


def read_file(filename: str, base_directory: str, encoding: str = 'utf-8') -> str:
    """
    Legge il contenuto di un file nella directory base.
    
    Args:
        filename: Nome del file da leggere
        base_directory: Percorso alla directory base di lavoro
        encoding: Encoding del file (default: utf-8)
        
    Returns:
        Contenuto del file come stringa
        
    Raises:
        FileNotFoundError: Se il file non esiste
        ValueError: Se il file non è valido, fuori dalla directory base, o è un file binario
        PermissionError: Se non si hanno permessi per leggere il file
        UnicodeDecodeError: Se il file non può essere decodificato
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
            
        # Controlla se è probabilmente un file binario
        if _is_likely_binary_file(file_path):
            file_size = file_path.stat().st_size
            size_str = _format_file_size(file_size)
            file_type = _get_file_type(file_path)
            raise ValueError(f"Cannot read {filename}: this appears to be a binary file ({file_type}, {size_str}). Binary files cannot be displayed as text.")
            
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
            
        return content
        
    except (FileNotFoundError, ValueError):
        # Re-raise questi errori specifici senza wrapping
        raise
    except PermissionError as e:
        raise PermissionError(f"Insufficient permissions to read {filename}: {e}")
    except UnicodeDecodeError as e:
        # Prova a determinare il tipo di file per un messaggio più chiaro
        try:
            base_path = Path(base_directory)
            file_path = base_path / filename
            file_type = _get_file_type(file_path)
            file_size = _format_file_size(file_path.stat().st_size)
            raise ValueError(f"Cannot read {filename}: this appears to be a {file_type} file ({file_size}) that cannot be decoded as text. Try using a file viewer appropriate for {file_type} files.")
        except Exception:
            raise UnicodeDecodeError(f"Cannot decode file {filename} with encoding {encoding}: {e}")


def _is_likely_binary_file(file_path: Path) -> bool:
    """
    Determina se un file è probabilmente binario basandosi su estensione e magic bytes.
    
    Args:
        file_path: Path del file da controllare
        
    Returns:
        True se il file è probabilmente binario
    """
    # Estensioni di file binari comuni
    binary_extensions = {
        '.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.rar', '.7z',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
        '.mp3', '.wav', '.flac', '.mp4', '.avi', '.mkv', '.mov',
        '.exe', '.dll', '.so', '.dylib', '.bin', '.dmg', '.iso',
        '.db', '.sqlite', '.sqlite3'
    }
    
    if file_path.suffix.lower() in binary_extensions:
        return True
    
    # Controlla i magic bytes (primi 1024 bytes per null bytes)
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            # Se contiene null bytes, è probabilmente binario
            if b'\x00' in chunk:
                return True
            
            # Per file di testo, verifichiamo se è decodificabile come UTF-8
            # Solo se non è decodificabile È probabilmente binario
            try:
                chunk.decode('utf-8')
                # Se si decodifica come UTF-8, è un file di testo
                return False
            except UnicodeDecodeError:
                # Se non si decodifica come UTF-8, è probabilmente binario
                # Ma potrebbe essere un encoding diverso, quindi non siamo sicuri al 100%
                return True
    except Exception:
        # Se non possiamo leggere, assumiamo sia sicuro provare come testo
        pass
    
    return False


def _get_file_type(file_path: Path) -> str:
    """Determina il tipo di file per messaggi più informativi."""
    extension = file_path.suffix.lower()
    
    type_map = {
        '.pdf': 'PDF document',
        '.docx': 'Word document', '.doc': 'Word document',
        '.xlsx': 'Excel spreadsheet', '.xls': 'Excel spreadsheet',
        '.pptx': 'PowerPoint presentation', '.ppt': 'PowerPoint presentation',
        '.zip': 'ZIP archive', '.rar': 'RAR archive', '.7z': '7-Zip archive',
        '.jpg': 'JPEG image', '.jpeg': 'JPEG image', '.png': 'PNG image',
        '.gif': 'GIF image', '.bmp': 'Bitmap image', '.tiff': 'TIFF image',
        '.mp3': 'MP3 audio', '.wav': 'WAV audio', '.flac': 'FLAC audio',
        '.mp4': 'MP4 video', '.avi': 'AVI video', '.mkv': 'MKV video',
        '.exe': 'executable', '.dll': 'dynamic library', '.so': 'shared library'
    }
    
    return type_map.get(extension, f"{extension[1:]} file" if extension else "binary file")


def _format_file_size(size_bytes: int) -> str:
    """Formatta la dimensione del file in formato human-readable."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB" 