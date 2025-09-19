from rich.console import Console

from byte.context import make
from byte.core.command.registry import CommandRegistry
from byte.core.response.handler import ResponseHandler
from byte.domain.agent.service import AgentService


class CommandProcessor:
    """Processes user input and routes commands to appropriate handlers.

    Distinguishes between slash commands (/add, /drop) and regular chat input,
    automatically including file context for non-command input to provide
    relevant context to the AI assistant.
    """

    def __init__(self, container):
        # Container provides access to file service and other dependencies
        self.container = container

        # TODO: This should be set from a config option.
        self._current_agent = "coder"

    def set_active_agent(self, agent_name: str) -> None:
        """Update the active agent for regular input processing."""
        self._current_agent = agent_name

    async def process_input(self, user_input: str) -> None:
        """Process user input and execute commands if applicable.

        Routes slash commands to command handlers, while regular input gets
        enhanced with file context for better AI responses.
        Usage: `await processor.process_input("/add file.py")` or `await processor.process_input("How do I fix this bug?")`
        """
        user_input = user_input.strip()

        if user_input.startswith("/"):
            await self._process_slash_command(user_input[1:])
        else:
            # Enhance regular input with file context for better AI responses
            await self._process_regular_input(user_input)

    async def _process_slash_command(self, command_text: str) -> None:
        """Parse and execute slash commands with their arguments.

        Splits command name from arguments and delegates to registered command handlers.
        """
        command_registry = await make(CommandRegistry)
        if " " in command_text:
            cmd_name, args = command_text.split(" ", 1)
        else:
            cmd_name, args = command_text, ""

        command = command_registry.get_slash_command(cmd_name)
        console = await make(Console)

        if command:
            await command.execute(args)
        else:
            console.print(f"[error]Unknown slash command: /{cmd_name}[/error]")

    async def _process_regular_input(self, user_input: str) -> None:
        """Route regular input to the currently active agent."""
        agent_service = await make(AgentService)

        response_handler = await make(ResponseHandler)

        await response_handler.handle_stream(
            agent_service.route_to_agent(self._current_agent, user_input)
        )
