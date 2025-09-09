import asyncio

from rich.console import Console

from bytesmith.prompt import PromptHandler


class ByteSmith:
    def __init__(self):
        self.console = Console()
        self.prompt_handler = PromptHandler()

    async def run_async(self):
        """Main CLI loop."""
        self.console.print("[bold blue]ByteSmith CLI Assistant[/bold blue]")
        self.console.print("Type 'exit' or 'quit' to leave\n")

        while True:
            try:
                user_input = await self.prompt_handler.get_input_async("bytesmith> ")

                if not user_input.strip():
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                # For now, just echo the input
                self.console.print(f"You said: {user_input}")

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
