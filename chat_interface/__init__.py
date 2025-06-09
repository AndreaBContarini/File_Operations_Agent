"""
Package chat_interface per interfacce utente del FileOperationsAgent.
Contiene implementazioni CLI e potenziali altre interfacce.
"""

from .cli import FileAgentCLI, create_sample_files

__all__ = [
    'FileAgentCLI',
    'create_sample_files'
] 