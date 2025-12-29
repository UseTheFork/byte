from typing import List, Type

from byte.core import Service, ServiceProvider
from byte.domain.cli import Command
from byte.domain.memory import ClearCommand, MemoryService, ResetCommand


class MemoryServiceProvider(ServiceProvider):
    """Service provider for conversation memory management.

    Registers memory services for short-term conversation persistence using
    LangGraph checkpointers. Enables stateful conversations and thread
    management for the AI agent system.
    Usage: Register with container to enable conversation memory
    """

    def services(self) -> List[Type[Service]]:
        return [MemoryService]

    def commands(self) -> List[Type[Command]]:
        return [ClearCommand, ResetCommand]
