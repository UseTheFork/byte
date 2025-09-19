import asyncio

from rich.console import Console

from byte.bootstrap import bootstrap, shutdown
from byte.container import Container
from byte.context import container_context
from byte.core.cli import cli
from byte.core.command.processor import CommandProcessor
from byte.core.config.config import ByteConfg
from byte.core.ui.prompt import PromptHandler
from byte.domain.agent.service import AgentService
from byte.domain.events.dispatcher import EventDispatcher
from byte.domain.system.events import ExitRequested, PrePrompt, PromptRefresh


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
        self._refresh_queue = asyncio.Queue(maxsize=10)

    async def initialize(self):
        """Initialize async resources and event listeners."""
        # Initialize prompt handler
        await self.prompt_handler.initialize()

        # Listen for exit and refresh events
        event_dispatcher = await self.container.make(EventDispatcher)
        event_dispatcher.listen(ExitRequested, self._handle_exit_request)
        event_dispatcher.listen(PromptRefresh, self._handle_prompt_refresh)

    def _handle_exit_request(self, event: ExitRequested):
        """Handle exit request by setting exit flag.

        Usage: Called automatically when ExitRequested event is emitted
        """
        self._should_exit = True

    def _handle_prompt_refresh(self, event: PromptRefresh):
        """Handle prompt refresh request by queuing it instead of immediate refresh.

        Usage: Called automatically when PromptRefresh event is emitted
        """
        try:
            # Non-blocking put - if queue is full, we'll just drop the event
            self._refresh_queue.put_nowait(event)
        except asyncio.QueueFull:
            # Queue is full, ignore this refresh request
            # This prevents memory issues if many refresh events pile up
            pass

    async def _check_for_refresh(self):
        """Check if there are any queued refresh events."""
        try:
            # Non-blocking get - returns immediately if queue is empty
            refresh_event = self._refresh_queue.get_nowait()
            return refresh_event
        except asyncio.QueueEmpty:
            return None

    async def cleanup(self):
        """Clean up application resources."""
        await shutdown(self.container)

    async def run(self):
        """Main CLI loop that handles user interaction and command execution.

        Uses async/await to prevent blocking on user input while maintaining
        responsive command execution and graceful shutdown handling.
        """
        await self.initialize()

        console: Console = await self.container.make(Console)
        event_dispatcher = await self.container.make(EventDispatcher)

        try:
            while not self._should_exit:
                try:
                    # Check for any queued refresh events before starting new prompt
                    refresh_event = await self._check_for_refresh()
                    if refresh_event:
                        console.print(f"[dim]{refresh_event.reason}[/dim]")
                        # Continue to show the updated prompt

                    # Allow commands to display contextual information before each prompt
                    agent_service: AgentService = await self.container.make(
                        AgentService
                    )
                    current_agent = agent_service.get_active_agent()
                    agent = await self.container.make(current_agent)

                    await event_dispatcher.dispatch(
                        PrePrompt(current_agent=current_agent)
                    )

                    # Get user input (this can now be interrupted safely)
                    user_input = await self.prompt_handler.get_input_async(
                        f"[{agent.name}]> "
                    )

                    if not user_input.strip():
                        continue

                    # Process the command
                    await self.command_processor.process_input(user_input)

                    # Check if exit was requested after processing
                    if self._should_exit:
                        break

                except KeyboardInterrupt:
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
