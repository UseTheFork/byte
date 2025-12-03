from langchain.messages import HumanMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.graph.state import END, RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.event_bus import EventType, Payload
from byte.core.utils.get_last_message import get_last_message
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

        # This is where we promote `scratch_messages` to `history_messages`
        update_dict = {
            **state,
            # We always want to erase the current user request
            "user_request": "",
        }

        # Only update messages if there are scratch messages to process
        if state["scratch_messages"]:
            last_message = get_last_message(state["scratch_messages"])
            clear_scratch = RemoveMessage(id=REMOVE_ALL_MESSAGES)

            # Create a HumanMessage from the user_request
            user_message = HumanMessage(content=state["user_request"])

            update_dict["history_messages"] = [user_message, last_message]
            update_dict["scratch_messages"] = clear_scratch

        return Command(
            goto=END,
            update=update_dict,
        )
