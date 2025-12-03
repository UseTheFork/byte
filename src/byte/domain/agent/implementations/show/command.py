from argparse import Namespace

from byte.domain.agent.implementations.show.agent import ShowAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command


class ShowCommand(Command):
    """Command to display the current conversation history and context.

    Invokes the ShowAgent to render the conversation state, including
    messages, file context, and other relevant information without
    making any modifications or AI calls.
    Usage: `/show` -> displays current conversation state
    """

    @property
    def name(self) -> str:
        return "show"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Display the current conversation history and context",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the Show agent to display conversation state.

        Invokes the ShowAgent through the agent service to render the current
        conversation history and context without making any modifications.

        Args:
            args: Unused for this command (empty string expected)

        Usage: Called automatically when user types `/show`
        """
        agent_service = await self.make(AgentService)
        await agent_service.execute_agent("", ShowAgent)
