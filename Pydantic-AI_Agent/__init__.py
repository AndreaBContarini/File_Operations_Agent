"""
Agent Pydantic-AI Hybrid package for file operations.
Hybrid implementation using Pydantic-AI framework with dual-model architecture:
- OpenAI GPT-4o for file operations
- Groq llama-3.1-8b-instant for query validation (optional)
"""

from .pydantic_agent import PydanticFileAgent
from .dependencies import AgentDependencies
from .models import AgentResponse

__all__ = [ # __all__ è una lista di stringhe che contiene i nomi degli oggetti che vogliamo esportare
    'PydanticFileAgent',
    'AgentDependencies', 
    'AgentResponse'
] 