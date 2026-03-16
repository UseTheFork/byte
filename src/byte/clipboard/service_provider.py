from typing import List, Type

from byte import Command, Service, ServiceProvider
from byte.clipboard import ClipboardService, CopyCommand, CopyDropCommand


class ClipboardServiceProvider(ServiceProvider):
    """Service provider for clipboard operations and file copying functionality.

    Registers the clipboard service for managing copy operations and provides
    commands for copying files and dropping file context from the clipboard.
    """

    def services(self) -> List[Type[Service]]:
        """Register clipboard-related services.

        Returns:
            List containing ClipboardService for managing copy operations.
        """
        return [
            ClipboardService,
        ]

    def commands(self) -> List[Type[Command]]:
        """Register clipboard-related commands.

        Returns:
            List of commands for copying files and managing clipboard context.
        """
        return [
            # keep-sorted start
            CopyCommand,
            CopyDropCommand,
            # keep-sorted end
        ]
