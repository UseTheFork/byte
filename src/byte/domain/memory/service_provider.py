from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.memory.command.clear_command import ClearCommand
from byte.domain.memory.command.reset_command import ResetCommand
from byte.domain.memory.service.memory_service import MemoryService


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
