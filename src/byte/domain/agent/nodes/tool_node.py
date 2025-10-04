import json

from langchain_core.messages import ToolMessage
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from byte.core.mixins.user_interactive import UserInteractive
from byte.domain.agent.nodes.base_node import Node


class ToolNode(Node, UserInteractive):
    async def boot(self, tools: list, **kwargs):
        self.tools_by_name = {tool.name: tool for tool in tools}

    async def __call__(self, inputs):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []

        for tool_call in message.tool_calls:
            console = await self.make(Console)

            pretty = Pretty(tool_call)
            console.print(Panel(pretty))

            run_tool = await self.prompt_for_confirmation(
                f"Use {tool_call['name']}", True
            )

            if run_tool:
                tool_result = await self.tools_by_name[tool_call["name"]].ainvoke(
                    tool_call["args"]
                )
            else:
                tool_result = {"result": "User declined tool call."}

            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}
