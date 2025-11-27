from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.prompt_format.command.copy_command import CopyCommand
from byte.domain.prompt_format.service.edit_format_service import EditFormatService
from byte.domain.prompt_format.service.parser_service import ParserService
from byte.domain.prompt_format.service.shell_command_service import ShellCommandService


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

    def commands(self) -> List[Type[Command]]:
        return [
            CopyCommand,
        ]
