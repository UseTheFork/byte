from langgraph.graph.state import END, RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.event_bus import EventType, Payload
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState


class EndNode(Node):
	async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
		if runtime is not None and runtime.context is not None:
			payload = Payload(
				event_type=EventType.END_NODE,
				data={
					"state": state,
					"agent": runtime.context.agent,
				},
			)
			await self.emit(payload)

		return Command(goto=END, update=state)
