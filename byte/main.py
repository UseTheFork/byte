import asyncio
from typing import TYPE_CHECKING

from byte.bootstrap import bootstrap
from byte.core.command.processor import CommandProcessor
from byte.core.command.registry import command_registry
from byte.core.ui.prompt import PromptHandler

if TYPE_CHECKING:
    from rich.console import Console


class Byte:
    def __init__(self, container):
        self.container = container
        self.prompt_handler = PromptHandler()
        self.command_processor = CommandProcessor(container)

    async def run_async(self):
        """Main CLI loop."""
        console: Console = self.container.make("console")

        while True:
            try:
                # Display pre-prompt information from all commands
                command_registry.pre_prompt()

                user_input = await self.prompt_handler.get_input_async("> ")

                if not user_input.strip():
                    continue

                # Process input through command system
                response = await self.command_processor.process_input(user_input)

                # Handle exit command
                if response == "EXIT_REQUESTED":
                    console.print("[warning]Goodbye![/warning]")
                    break

            except KeyboardInterrupt:
                console.print("\n[warning]Goodbye![/warning]")
                break

    def run(self):
        """Run the async CLI loop."""
        asyncio.run(self.run_async())


def main():
    # Bootstrap the application and get the container
    container = bootstrap()
    app = Byte(container)
    app.run()


if __name__ == "__main__":
    main()
