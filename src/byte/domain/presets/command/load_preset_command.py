from argparse import Namespace
from typing import List

from byte.core.config.config import ByteConfg
from byte.domain.analytics.service.agent_analytics_service import AgentAnalyticsService
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.cli.service.prompt_toolkit_service import PromptToolkitService
from byte.domain.files.models import FileMode
from byte.domain.files.service.file_service import FileService
from byte.domain.knowledge.service.convention_context_service import ConventionContextService
from byte.domain.memory.service.memory_service import MemoryService


class LoadPresetCommand(Command):
    """Command to load a predefined preset configuration.

    Loads a preset by ID, optionally clearing conversation history, and configures
    the context with specified files and conventions. Presets enable quick switching
    between different project configurations.
    Usage: `/preset my-preset` -> loads preset configuration
    """

    @property
    def name(self) -> str:
        return "preset"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Load a predefined preset configuration with files and conventions",
        )

        parser.add_argument("preset_id", help="ID of the preset to load")
        parser.add_argument(
            "--should-not-clear-history",
            action="store_true",
            help="Do not clear conversation history before loading preset",
        )
        parser.add_argument(
            "--should-not-clear-files", action="store_true", help="Do not clear file context before loading preset"
        )
        parser.add_argument(
            "--silent",
            action="store_true",
            help="Run silently without prompting for confirmations",
        )

        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Load a preset configuration by ID.

        Validates the preset exists, optionally clears conversation history,
        clears current file context, adds preset files (read-only and editable),
        and loads preset conventions.
        """
        console = await self.make(ConsoleService)

        preset_id = args.preset_id

        # Validate preset ID and retrieve preset configuration
        config = await self.make(ByteConfg)
        if config.presets:
            preset = next((p for p in config.presets if p.id == preset_id), None)

        if preset is None:
            console.print_error(f"Preset '{preset_id}' not found")
            return

        # Prompt user to confirm clearing history before loading preset
        if not args.should_not_clear_history:
            should_clear = await self.prompt_for_confirmation(
                "Would you like to clear the conversation history before loading this preset?", default=True
            )

            if should_clear:
                memory_service = await self.make(MemoryService)
                await memory_service.new_thread()

                agent_analytics_service = await self.make(AgentAnalyticsService)
                agent_analytics_service.reset_context()
                console.print_info("History cleared")

        file_service = await self.make(FileService)

        if not args.should_not_clear_files:
            should_clear_files = await self.prompt_for_confirmation(
                "Would you like to clear the file context before loading this preset?", default=False
            )

            if should_clear_files:
                await file_service.clear_context()

        for file_path in preset.read_only_files:
            await file_service.add_file(file_path, FileMode.READ_ONLY)

        for file_path in preset.editable_files:
            await file_service.add_file(file_path, FileMode.EDITABLE)

        convention_service = await self.make(ConventionContextService)
        convention_service.clear_conventions()

        for convention_filename in preset.conventions:
            convention_service.add_convention(convention_filename)

        if preset.prompt is not None:
            prompt_service = await self.make(PromptToolkitService)
            prompt_service.set_placeholder(preset.prompt)

        if not args.silent:
            console.print_success(f"Preset '{preset_id}' loaded successfully")

    async def get_completions(self, text: str) -> List[str]:
        """Return tab completion suggestions for preset IDs.

        Usage: return ["foo", "bar"] for available preset IDs
        """
        config = await self.make(ByteConfg)
        if config.presets:
            preset_ids = [preset.id for preset in config.presets]

        # Filter preset IDs that start with the input text
        return [preset_id for preset_id in preset_ids if preset_id.startswith(text)]
