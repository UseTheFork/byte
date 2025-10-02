from byte.domain.agent.implementations.ask.agent import AskAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.service.command_registry import Command


class AskCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "ask"

    @property
    def description(self) -> str:
        return ""

    async def execute(self, args: str) -> None:
        """ """
        agent_service = await self.make(AgentService)
        await agent_service.execute_agent([("user", args)], AskAgent)
