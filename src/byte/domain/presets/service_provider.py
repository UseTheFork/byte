from typing import List, Type

from byte.container import Container
from byte.core.config.config import ByteConfg
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.presets.command.load_preset_command import LoadPresetCommand
from byte.domain.presets.command.save_preset_command import SavePresetCommand


class PresetsProvider(ServiceProvider):
    """Service provider for preset management functionality.

    Registers the LoadPresetCommand which allows users to quickly load
    predefined sets of files into context using the /preset command.
    """

    def commands(self) -> List[Type[Command]]:
        return [
            LoadPresetCommand,
            SavePresetCommand,
        ]

    def services(self) -> List[Type[Service]]:
        return []

    async def boot(self, container: Container) -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """

        load_preset_command = await container.make(LoadPresetCommand)

        config = await container.make(ByteConfg)
        if config.presets:
            for preset in config.presets:
                if preset.load_on_boot:
                    await load_preset_command.handle(
                        f"{preset.id} --should-not-clear-history --should-not-clear-files --silent"
                    )
                    break
