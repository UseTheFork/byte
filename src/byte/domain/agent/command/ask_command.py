from byte.domain.agent.implementations.ask.agent import AskAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.service.command_registry import Command


class AskCommand(Command):
	"""Command to execute the Ask agent for general questions and assistance.

	Allows users to ask questions or request assistance from the AI agent,
	processing natural language queries through the agent service.
	Usage: `/ask How do I implement error handling?` -> executes Ask agent
	"""

	@property
	def name(self) -> str:
		return "ask"

	@property
	def description(self) -> str:
		return "Ask the AI agent a question or request assistance"

	async def execute(self, args: str) -> None:
		"""Execute the Ask agent with the provided user query.

		Processes the user's question through the agent service, which handles
		the complete interaction flow including AI response generation and display.

		Args:
			args: The user's question or query text

		Usage: Called automatically when user types `/ask <question>`
		"""
		agent_service = await self.make(AgentService)
		await agent_service.execute_agent({"messages": [("user", args)]}, AskAgent)
