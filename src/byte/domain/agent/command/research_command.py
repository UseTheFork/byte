from langgraph.graph.state import RunnableConfig
from typing_extensions import cast

from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.agent.implementations.research.agent import ResearchAgent
from byte.domain.agent.nodes.extract_node import SessionContextFormatter
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.service.command_registry import Command
from byte.domain.knowledge.models import SessionContextModel
from byte.domain.knowledge.service.session_context_service import SessionContextService
from byte.domain.memory.service.memory_service import MemoryService


class ResearchCommand(Command):
	"""Execute the research agent to gather codebase insights and information.

	Invokes the research agent to analyze code, find patterns, and provide
	detailed findings that are saved to the session context for other agents.
	Usage: `research "How is error handling implemented?"`
	"""

	@property
	def name(self) -> str:
		return "research"

	@property
	def category(self) -> str:
		return "Agent"

	@property
	def description(self) -> str:
		return "Execute research agent to gather codebase insights, analyze patterns, and save detailed findings to session context for other agents"

	async def execute(self, args: str) -> None:
		"""Execute research agent with the given query.

		Runs the research agent to investigate the codebase based on the user's
		query, then saves the formatted findings to the session context.

		Args:
			args: The research query or question to investigate

		Usage: `await command.execute("How is authentication handled?")`
		"""
		coder_agent = await self.make(CoderAgent)
		coder_agent_graph = await coder_agent.get_graph()

		memory_service = await self.make(MemoryService)
		thread_id = await memory_service.get_or_create_thread()

		config = RunnableConfig(configurable={"thread_id": thread_id})
		state_snapshot = await coder_agent_graph.aget_state(config)
		messages = state_snapshot.values.get("messages", [])

		agent_service = await self.make(AgentService)
		agent_result = await agent_service.execute_agent({"messages": [*messages, ("user", args)]}, ResearchAgent)

		extracted_content = cast(SessionContextFormatter, agent_result.get("extracted_content"))

		session_context_service = await self.make(SessionContextService)
		model = await self.make(
			SessionContextModel, type="agent", key=extracted_content.name, content=extracted_content.content
		)
		session_context_service.add_context(model)
