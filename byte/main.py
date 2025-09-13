import asyncio
from typing import TYPE_CHECKING

from byte.bootstrap import bootstrap
from byte.core.command.processor import CommandProcessor
from byte.core.command.registry import command_registry
from byte.core.ui.prompt import PromptHandler
from byte.domain.system.events import ExitRequested

if TYPE_CHECKING:
    from rich.console import Console


class Byte:
    """Main application class that orchestrates the CLI interface and command processing.

    Separates concerns by delegating prompt handling to PromptHandler and command
    processing to CommandProcessor, while maintaining the main event loop.
    """

    def __init__(self, container):
        self.container = container
        self.prompt_handler = PromptHandler()
        self.command_processor = CommandProcessor(container)
        self._should_exit = False

        # Listen for exit events
        event_dispatcher = container.make("event_dispatcher")
        event_dispatcher.listen("ExitRequested", self._handle_exit_request)

    def _handle_exit_request(self, event: ExitRequested):
        """Handle exit request by setting exit flag.

        Usage: Called automatically when ExitRequested event is emitted
        """
        self._should_exit = True

    async def run_async(self):
        """Main CLI loop that handles user interaction and command execution.

        Uses async/await to prevent blocking on user input while maintaining
        responsive command execution and graceful shutdown handling.
        """
        console: Console = self.container.make("console")

        while not self._should_exit:
            try:
                # Allow commands to display contextual information before each prompt
                command_registry.pre_prompt()

                user_input = await self.prompt_handler.get_input_async("> ")

                if not user_input.strip():
                    continue

                # Process input without expecting return value
                await self.command_processor.process_input(user_input)

                # Check if exit was requested after processing
                if self._should_exit:
                    break

            except KeyboardInterrupt:
                console.print("\n[warning]Goodbye![/warning]")
                break

        console.print("[warning]Goodbye![/warning]")

    def run(self):
        """Synchronous entry point that wraps the async event loop.

        Provides a clean interface for callers who don't need async context.
        """
        asyncio.run(self.run_async())


def main():
    """Application entry point that bootstraps dependencies and starts the CLI.

    Follows dependency injection pattern by bootstrapping the container first,
    then injecting it into the main application class.
    """
    container = bootstrap()
    app = Byte(container)
    app.run()


if __name__ == "__main__":
    main()
