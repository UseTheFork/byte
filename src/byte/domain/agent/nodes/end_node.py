from langchain_core.messages import HumanMessage
from langgraph.graph.message import RemoveMessage
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

        # If we have errors we need to remove AI messages that were used to `course correct` the errors
        if state.get("errors") is not None:
            messages = state.get("messages", [])

            # Find the last HumanMessage index
            last_human_index = None
            for i in range(len(messages) - 1, -1, -1):
                if isinstance(messages[i], HumanMessage):
                    last_human_index = i
                    break

            # If we found a HumanMessage and there are messages after it
            if last_human_index is not None and last_human_index + 1 < len(messages):
                # Keep the first AI message after the HumanMessage (index last_human_index + 1)
                # Remove all messages after that (starting from last_human_index + 2)
                messages_to_remove = []
                for i in range(last_human_index + 2, len(messages)):
                    messages_to_remove.append(RemoveMessage(id=messages[i].id))

                if messages_to_remove:
                    state["messages"] = messages_to_remove

            state["errors"] = None

        return Command(goto=END, update={**state})
