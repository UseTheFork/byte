# nodes/assistant_node.py
from langgraph.graph.state import Runnable

from byte.domain.agent.nodes.base_node import Node


class AssistantNode(Node):
    async def boot(self, runnable: Runnable, **kwargs):
        self.runnable = runnable

    async def __call__(self, state, config):
        while True:
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
