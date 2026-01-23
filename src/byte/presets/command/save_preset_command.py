from argparse import Namespace

from byte.cli import ByteArgumentParser, Command
from byte.files import FileMode, FileService
from byte.knowledge import ConventionContextService
from byte.presets import PresetsConfig
from byte.support.utils.slugify import slugify
from byte.system import ConfigWriterService


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

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Save the current context as a new preset.

        Prompts user for a preset name, collects current files and conventions,
        creates a new preset configuration, and adds it to the config.
        """
        console = self.app["console"]

        # Prompt for preset name
        preset_name = await self.prompt_for_input("Enter a name for this preset")

        if not preset_name:
            console.print_error("Preset name cannot be empty")
            return

        # Slugify the preset name to ensure it's URL-safe
        preset_id = slugify(preset_name)

        # Check if preset with this ID already exists
        config = self.app["config"]
        if config.presets:
            existing_preset = next((p for p in config.presets if p.id == preset_id), None)
            if existing_preset:
                console.print_error(f"Preset with ID '{preset_id}' already exists")
                return

        # Get current file context
        file_service = self.app.make(FileService)
        read_only_files = [f.relative_path for f in file_service.list_files(FileMode.READ_ONLY)]
        editable_files = [f.relative_path for f in file_service.list_files(FileMode.EDITABLE)]

        # Get current conventions
        convention_service = self.app.make(ConventionContextService)
        conventions = list(convention_service.get_conventions().keys())

        # Prompt for optional default prompt text
        preset_prompt = await self.prompt_for_input("Enter a default prompt for this preset (leave blank to skip)")

        # Only include prompt if user provided one
        prompt_value = preset_prompt if preset_prompt and preset_prompt.strip() else None

        # Create new preset configuration
        new_preset = PresetsConfig(
            id=preset_id,
            read_only_files=read_only_files,
            editable_files=editable_files,
            conventions=conventions,
            prompt=prompt_value,
        )

        # Add preset to config
        if config.presets is None:
            config.presets = []
        config.presets.append(new_preset)

        # Persist preset to config.yaml file
        config_writer = self.app.make(ConfigWriterService)
        await config_writer.append_preset(new_preset)

        console.print_success(f"Preset '{preset_id}' saved successfully")
