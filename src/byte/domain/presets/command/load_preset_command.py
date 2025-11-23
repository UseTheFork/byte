from typing import List

from byte.core.config.config import ByteConfg
from byte.domain.analytics.service.agent_analytics_service import AgentAnalyticsService
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
    def description(self) -> str:
        return "Load a predefined preset configuration with files and conventions"

    async def execute(self, args: str) -> None:
        """Load a preset configuration by ID.

        Validates the preset exists, optionally clears conversation history,
        clears current file context, adds preset files (read-only and editable),
        and loads preset conventions.

        Args:
            args: Preset ID to load

        Usage: `await command.execute("my-preset")` -> loads preset with ID "my-preset"
        """
        console = await self.make(ConsoleService)

        if not args:
            console.print("Usage: /preset <id>")
            return

        # Validate preset ID and retrieve preset configuration
        config = await self.make(ByteConfg)
        if config.presets:
            preset = next((p for p in config.presets if p.id == args), None)

        if preset is None:
            console.print_error(f"Preset '{args}' not found")
            return

        # Prompt user to confirm clearing history before loading preset
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

        if preset.prompt:
            prompt_service = await self.make(PromptToolkitService)
            prompt_service.set_placeholder(preset.prompt)

        console.print_success(f"Preset '{args}' loaded successfully")

    async def get_completions(self, text: str) -> List[str]:
        """Return tab completion suggestions for preset IDs.

        Usage: return ["foo", "bar"] for available preset IDs
        """
        config = await self.make(ByteConfg)
        if config.presets:
            preset_ids = [preset.id for preset in config.presets]

        # Filter preset IDs that start with the input text
        return [preset_id for preset_id in preset_ids if preset_id.startswith(text)]
