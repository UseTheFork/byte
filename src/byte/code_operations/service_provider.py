from typing import List, Type

from byte import Service, ServiceProvider
from byte.code_operations import EditFormatService, ParserService, ShellCommandService


class PromptFormatProvider(ServiceProvider):
    """Service provider for edit format and code block processing functionality.

    Registers services for parsing and applying SEARCH/REPLACE blocks and shell
    commands from AI responses. Manages the edit block lifecycle and integrates
    with the event system for message preprocessing.
    Usage: Register with container to enable edit format processing
    """

    def services(self) -> List[Type[Service]]:
        return [
            EditFormatService,
            ParserService,
            ShellCommandService,
        ]
