import json

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.node import BaseNode
from byte.orchestration import AssistantContextSchema, BaseState
from byte.support.utils import get_last_message
from byte.tui import Messages


class ToolNode(BaseNode):
    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[str]:
        message = get_last_message(state["scratch_messages"])

        outputs = []

        tools = runtime.context.tools

        # Check if tools are available
        if not tools:
            return self.route_back(state, {"scratch_messages": []})

        # Build a mapping of tool names to tool instances
        tools_by_name = {tool.name: tool for tool in tools}

        for tool_call in message.tool_calls:
            # Check if the tool exists
            if tool_call["name"] not in tools_by_name:
                outputs.append(
                    ToolMessage(
                        content=f"Error: Tool '{tool_call['name']}' is not available or does not exist.",
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
                continue

            # Emit tool call to TUI
            await self.emit_tui(
                Messages.ToolCall(
                    name=tool_call["name"],
                    args=tool_call["args"],
                )
            )

            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])

            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return self.route_back(state, {"scratch_messages": outputs})
