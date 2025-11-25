from argparse import Namespace

from byte.core.config.config import ByteConfg
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.service.file_service import FileService
from byte.domain.knowledge.service.convention_context_service import ConventionContextService
from byte.domain.presets.config import PresetsConfig


class SavePresetCommand(Command):
    """Command to save the current context as a preset configuration.

    Captures the current file context (read-only and editable files) and loaded
    conventions, prompts for a preset name, and adds the configuration to the
    config file for future use.
    Usage: `/preset:save` -> saves current context as a preset
    """

    @property
    def name(self) -> str:
        return "preset:save"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Save the current context as a preset configuration",
        )
        return parser

    async def execute(self, args: Namespace) -> None:
        """Save the current context as a new preset.

        Prompts user for a preset name, collects current files and conventions,
        creates a new preset configuration, and adds it to the config.
        """
        console = await self.make(ConsoleService)

        # Prompt for preset name
        preset_name = await self.prompt_for_input("Enter a name for this preset:")

        if not preset_name:
            console.print_error("Preset name cannot be empty")
            return

        # Get current file context
        file_service = await self.make(FileService)
        read_only_files = [f.relative_path for f in file_service.list_files()]
        editable_files = [f.relative_path for f in file_service.list_files()]

        # Get current conventions
        convention_service = await self.make(ConventionContextService)
        conventions = list(convention_service.get_conventions().keys())

        # Create new preset configuration
        new_preset = PresetsConfig(
            id=preset_name,
            read_only_files=read_only_files,
            editable_files=editable_files,
            conventions=conventions,
        )

        # Add preset to config
        config = await self.make(ByteConfg)
        if config.presets is None:
            config.presets = []
        config.presets.append(new_preset)

        console.print_success(f"Preset '{preset_name}' saved successfully")
