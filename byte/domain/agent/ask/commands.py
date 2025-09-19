from rich.console import Console

from byte.core.command.registry import Command
from byte.core.response.handler import ResponseHandler
from byte.domain.agent.ask.service import AskAgent


class AskCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "ask"

    @property
    def description(self) -> str:
        return "Get coding assistance from the specialized coder agent"

    async def execute(self, args: str) -> None:
        """Execute coder request and stream response to console.

        Processes the user's coding request through the coder agent,
        streaming the response in real-time for immediate feedback.
        Usage: Called by command processor when user types `/coder <request>`
        """
        console: Console = await self.make(Console)

        if not args.strip():
            console.print("[warning]Please provide a coding request.[/warning]")
            console.print("Usage: /coder <your coding request>")
            return

        coder_service = await self.make(AskAgent)

        response_handler = await self.make(ResponseHandler)

        # Stream coder agent response through centralized handler
        await response_handler.handle_stream(coder_service.stream(args))
