import asyncio
from typing import TYPE_CHECKING

from byte.bootstrap import bootstrap
from byte.core.command.processor import CommandProcessor
from byte.core.command.registry import command_registry
from byte.core.ui.prompt import PromptHandler

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

    async def run_async(self):
        """Main CLI loop that handles user interaction and command execution.
        
        Uses async/await to prevent blocking on user input while maintaining
        responsive command execution and graceful shutdown handling.
        """
        console: Console = self.container.make("console")

        while True:
            try:
                # Allow commands to display contextual information before each prompt
                command_registry.pre_prompt()

                user_input = await self.prompt_handler.get_input_async("> ")

                if not user_input.strip():
                    continue

                # Delegate all input processing to maintain separation of concerns
                response = await self.command_processor.process_input(user_input)

                # Use string-based exit signal to avoid tight coupling with exit command
                if response == "EXIT_REQUESTED":
                    console.print("[warning]Goodbye![/warning]")
                    break

            except KeyboardInterrupt:
                console.print("\n[warning]Goodbye![/warning]")
                break

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
