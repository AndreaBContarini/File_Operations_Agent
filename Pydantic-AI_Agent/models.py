"""
Modelli Pydantic, per structured output dell'agent.
Definisce le strutture dati validate per le risposte dell'agent.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """
    Struttura della risposta dell'agent con validazione Pydantic.
    
    Garantisce che l'output dell'agent sia sempre strutturato e validato,
    sostituendo il sistema di synthesis custom dell'implementazione originale.
    """
    success: bool = Field(description="Se l'operazione è stata completata con successo")
    message: str = Field(description="Messaggio principale della risposta")
    type: str = Field(description="Tipo di operazione eseguita")
    
    # Dati opzionali per diversi tipi di response
    files: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="Lista di file per operazioni di listing"
    )
    file_content: Optional[str] = Field(
        default=None, 
        description="Contenuto di un file per operazioni di lettura"
    )
    analysis_result: Optional[str] = Field(
        default=None, 
        description="Risultato di analisi intelligente sui file"
    )
    
    # Metadati dell'esecuzione
    operations_performed: Optional[List[str]] = Field(
        default=None, 
        description="Lista delle operazioni eseguite dall'agent"
    )
    reasoning: Optional[str] = Field(
        default=None, 
        description="Reasoning dell'agent per le operazioni eseguite"
    )


class FileInfo(BaseModel):
    """Modello per informazioni su un singolo file."""
    name: str
    size: int
    modified: float
    extension: str
    is_directory: bool = False


class ValidationError(BaseModel):
    """Modello per errori di validazione."""
    error_type: str
    message: str
    help_text: Optional[str] = None 