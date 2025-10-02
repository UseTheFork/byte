from langgraph.graph.state import Runnable

from byte.core.event_bus import EventType, Payload
from byte.domain.agent.nodes.base_node import Node


class AssistantNode(Node):
    async def boot(self, runnable: Runnable, **kwargs):
        self.runnable = runnable

    async def __call__(self, state, config):
        while True:
            payload = Payload(
                event_type=EventType.PRE_ASSISTANT_NODE,
                data={
                    "state": state,
                    "config": config,
                },
            )

            payload = await self.emit(payload)
            state = payload.get("state", state)
            config = payload.get("config", config)

            result = await self.runnable.ainvoke(state, config=config)

            # Ensure we get a real response
            if not result.tool_calls and (
                not result.content
                or (
                    isinstance(result.content, list)
                    and not result.content[0].get("text")
                )
            ):
                # Re-prompt for actual response
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break

        return {"messages": [result]}
