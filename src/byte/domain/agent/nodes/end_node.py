from langgraph.graph.state import RunnableConfig

from byte.core.event_bus import EventType, Payload
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.state import BaseState


class EndNode(Node):
	async def boot(
		self,
		agent: str,
		llm,
		**kwargs,
	):
		self.agent = agent
		self.llm = llm

	async def __call__(self, state: BaseState, config: RunnableConfig):
		payload = Payload(
			event_type=EventType.END_NODE,
			data={
				"state": state,
				"agent": self.agent,
				"llm": self.llm,
			},
		)
		await self.emit(payload)

		return state
