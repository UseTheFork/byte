from byte.domain.agent.implementations.research.agent import ResearchAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.service.command_registry import Command


class ResearchCommand(Command):
	""" """

	@property
	def name(self) -> str:
		return "research"

	@property
	def category(self) -> str:
		return "Agent"

	@property
	def description(self) -> str:
		return ""

	async def execute(self, args: str) -> None:
		""" """
		agent_service = await self.make(AgentService)
		await agent_service.execute_agent({"messages": [("user", args)]}, ResearchAgent)
