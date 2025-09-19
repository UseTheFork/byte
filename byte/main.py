import asyncio

from rich.console import Console

from byte.bootstrap import bootstrap, shutdown
from byte.container import Container
from byte.context import container_context
from byte.core.cli import cli
from byte.core.command.processor import CommandProcessor
from byte.core.command.registry import CommandRegistry
from byte.core.config.config import ByteConfg
from byte.core.ui.prompt import PromptHandler
from byte.domain.agent.service import AgentService
from byte.domain.events.dispatcher import EventDispatcher
from byte.domain.system.events import ExitRequested


class Byte:
    """Main application class that orchestrates the CLI interface and command processing.

    Separates concerns by delegating prompt handling to PromptHandler and command
    processing to CommandProcessor, while maintaining the main event loop.
    """

    def __init__(self, container: Container):
        self.container = container
        container_context.set(self.container)
        self.prompt_handler = PromptHandler()
        self.command_processor = CommandProcessor(container)
        self._should_exit = False

    async def initialize(self):
        """Initialize async resources and event listeners."""
        # Listen for exit events
        event_dispatcher = await self.container.make(EventDispatcher)
        event_dispatcher.listen("ExitRequested", self._handle_exit_request)

    def _handle_exit_request(self, event: ExitRequested):
        """Handle exit request by setting exit flag.

        Usage: Called automatically when ExitRequested event is emitted
        """
        self._should_exit = True

    async def cleanup(self):
        """Clean up application resources."""
        await shutdown(self.container)

    async def run(self):
        """Main CLI loop that handles user interaction and command execution.

        Uses async/await to prevent blocking on user input while maintaining
        responsive command execution and graceful shutdown handling.
        """
        await self.initialize()

        # AI:
        console = await self.container.make(Console)
        command_registry = await self.container.make(CommandRegistry)

        try:
            while not self._should_exit:
                try:
                    # Allow commands to display contextual information before each prompt
                    await command_registry.pre_prompt()

                    agent_service: AgentService = await self.container.make(
                        AgentService
                    )
                    current_agent = agent_service.get_active_agent()
                    user_input = await self.prompt_handler.get_input_async(
                        f"[{current_agent}]> "
                    )

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
        finally:
            # Always cleanup before exit
            await self.cleanup()

        console.print("[warning]Goodbye![/warning]")


async def main(config: ByteConfg):
    """Application entry point that bootstraps dependencies and starts the CLI.

    Follows dependency injection pattern by bootstrapping the container first,
    then injecting it into the main application class.
    """
    container = await bootstrap(config)
    app = Byte(container)
    await app.run()


def run(config: ByteConfg):
    asyncio.run(main(config))


if __name__ == "__main__":
    cli()
