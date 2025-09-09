import asyncio

from rich.console import Console

from bytesmith.commands.processor import CommandProcessor
from bytesmith.commands.registry import command_registry
from bytesmith.ui.prompt import PromptHandler


class ByteSmith:
    def __init__(self):
        self.console = Console()
        self.prompt_handler = PromptHandler()
        self.command_processor = CommandProcessor()

    async def run_async(self):
        """Main CLI loop."""
        self.console.print("[bold blue]ByteSmith CLI Assistant[/bold blue]")
        self.console.print("Type 'exit', 'quit', or '/help' for commands\n")

        while True:
            try:
                # Display pre-prompt information from all commands
                command_registry.display_all_pre_prompt_info(self.console)
                
                user_input = await self.prompt_handler.get_input_async("> ")

                if not user_input.strip():
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

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
    app = ByteSmith()
    app.run()


if __name__ == "__main__":
    main()
