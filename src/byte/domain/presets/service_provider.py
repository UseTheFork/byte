from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.presets.command.load_preset_command import LoadPresetCommand


class PresetsProvider(ServiceProvider):
    """Service provider for preset management functionality.

    Registers the LoadPresetCommand which allows users to quickly load
    predefined sets of files into context using the /preset command.
    """

    def commands(self) -> List[Type[Command]]:
        return [
            LoadPresetCommand,
        ]

    def services(self) -> List[Type[Service]]:
        return []
