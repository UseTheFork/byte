from typing import List, Type

from byte import Command, Service, ServiceProvider
from byte.presets import LoadPresetCommand, SavePresetCommand


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

    async def boot(self) -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """

        load_preset_command = self.app.make(LoadPresetCommand)

        config = self.app.make("config")
        if config.presets:
            for preset in config.presets:
                if preset.load_on_boot:
                    await load_preset_command.handle(
                        f"{preset.id} --should-not-clear-history --should-not-clear-files --silent"
                    )
                    break
