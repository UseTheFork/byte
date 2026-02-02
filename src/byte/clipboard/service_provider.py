from typing import List, Type

from byte import Command, Service, ServiceProvider
from byte.clipboard import ClipboardService, CopyCommand, CopyDropCommand


class ClipboardServiceProvider(ServiceProvider):
    """Service provider for simplified file functionality with project discovery."""

    def services(self) -> List[Type[Service]]:
        return [
            ClipboardService,
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            # keep-sorted start
            CopyCommand,
            CopyDropCommand,
            # keep-sorted end
        ]
