import asyncio

from rich.console import Console

from byte.bootstrap import bootstrap
from byte.core.command.processor import CommandProcessor
from byte.core.command.registry import command_registry
from byte.core.ui.prompt import PromptHandler


class Byte:
    def __init__(self, container):
        self.container = container
        self.console = Console()
        self.prompt_handler = PromptHandler()
        self.command_processor = CommandProcessor(container)

    async def run_async(self):
        """Main CLI loop."""
        self.console.print("[bold blue]ByteSmith CLI Assistant[/bold blue]")
        self.console.print("Type 'exit', 'quit', or '/help' for commands\n")

        while True:
            try:
                # Display pre-prompt information from all commands
                command_registry.pre_prompt(self.console)

                user_input = await self.prompt_handler.get_input_async("> ")

                if not user_input.strip():
                    continue

                # Process input through command system
                response = await self.command_processor.process_input(user_input)

                # Handle exit command
                if response == "EXIT_REQUESTED":
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                self.console.print(response)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Goodbye![/yellow]")
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
