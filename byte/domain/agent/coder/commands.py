from typing import TYPE_CHECKING

from byte.core.command.registry import Command
from byte.core.response.handler import ResponseHandler
from byte.domain.agent.coder.service import CoderService

if TYPE_CHECKING:
    from rich.console import Console


class CoderCommand(Command):
    """Command to interact with the coder agent for software development assistance.

    Provides direct access to the specialized coder agent through slash commands,
    enabling users to request code generation, debugging, refactoring, and analysis
    with full file context integration and streaming responses.
    Usage: `/coder Fix the bug in main.py` -> streams coder agent response
    """

    @property
    def name(self) -> str:
        return "coder"

    @property
    def description(self) -> str:
        return "Get coding assistance from the specialized coder agent"

    async def execute(self, args: str) -> None:
        """Execute coder request and stream response to console.

        Processes the user's coding request through the coder agent,
        streaming the response in real-time for immediate feedback.
        Usage: Called by command processor when user types `/coder <request>`
        """
        console: Console = await self.container.make("console")

        if not args.strip():
            console.print("[warning]Please provide a coding request.[/warning]")
            console.print("Usage: /coder <your coding request>")
            return

        coder_service: CoderService = await self.container.make("coder_service")

        # Show that we're processing the request
        console.print()

        # try:
        # Use centralized response handler for consistent streaming

        response_handler: ResponseHandler = await self.container.make(
            "response_handler"
        )

        # Stream coder agent response through centralized handler
        await response_handler.handle_stream(coder_service.stream_code(args), console)

        # except Exception as e:
        #     console.print(f"[error]Error processing coder request:[/error] {e}")
