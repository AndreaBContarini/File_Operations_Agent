"""
Dependency injection per Pydantic-AI agent.
Definisce le dipendenze che verranno iniettate nell'agent context.
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentDependencies:
    """
    Dipendenze per l'agent Pydantic-AI.
    
    Contiene la directory base e altri parametri di configurazione
    che verranno iniettati nel RunContext dell'agent.
    """
    base_directory: str
    openai_api_key: str
    verbose: bool = False
    
    def __post_init__(self):
        """Valida e normalizza la directory base."""
        self.base_directory = str(Path(self.base_directory).resolve())
        
    @property
    def base_path(self) -> Path:
        """Restituisce la directory base come Path object."""
        return Path(self.base_directory) 