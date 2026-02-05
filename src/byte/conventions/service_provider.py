from typing import List, Type

from byte import Command, Service, ServiceProvider
from byte.conventions import ConventionCommand, ConventionContextService


class ConventionsServiceProvider(ServiceProvider):
    """Service provider for long-term knowledge management.

    Registers knowledge services for persistent storage of user preferences,
    project patterns, and learned behaviors. Enables cross-session memory
    and intelligent context building for the AI agent system.
    Usage: Register with container to enable long-term knowledge storage
    """

    def services(self) -> List[Type[Service]]:
        return [
            ConventionContextService,
        ]

    def commands(self) -> List[Type[Command]]:
        return [ConventionCommand]
