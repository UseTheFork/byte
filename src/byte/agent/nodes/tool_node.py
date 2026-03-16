import json
from typing import Literal

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, AssistantNode, BaseState, Node
from byte.cli.rich.byte_display import ByteDisplay
from byte.support import Str
from byte.support.mixins import UserInteractive
from byte.support.utils import get_last_message


class ToolNode(Node, UserInteractive):
    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["assistant_node"]]:
        message = get_last_message(state["scratch_messages"])

        outputs = []

        tools = runtime.context.tools

        # Check if tools are available
        if not tools:
            return Command(goto=Str.class_to_snake_case(AssistantNode), update={"scratch_messages": []})

        # Build a mapping of tool names to tool instances
        tools_by_name = {tool.name: tool for tool in tools}
        console = self.app["console"]

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

            # Format tool call information
            tool_info_lines = [f" {tool_call['name']}()"]
            for key, value in tool_call["args"].items():
                tool_info_lines.append(f" ╰- {key}: `{value}`")

            tool_display = ByteDisplay("\n".join(tool_info_lines), theme=console.syntax_theme)
            console.print(tool_display)

            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])

            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return Command(goto=Str.class_to_snake_case(AssistantNode), update={"scratch_messages": outputs})
