import json

from langchain_core.messages import ToolMessage
from langgraph.graph.message import RemoveMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from rich.pretty import Pretty
from rich.text import Text

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import get_last_message
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema, ConstraintSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService


class ToolNode(Node, UserInteractive):
    async def __call__(self, state: BaseState, runtime: Runtime[AssistantContextSchema]):
        message = get_last_message(state["scratch_messages"])

        outputs = []

        tools = runtime.context.tools

        # Check if tools are available
        if not tools:
            return Command(goto="assistant_node", update={"scratch_messages": []})

        # Build a mapping of tool names to tool instances
        tools_by_name = {tool.name: tool for tool in tools}

        for tool_call in message.tool_calls:
            console = await self.make(ConsoleService)

            pretty = Pretty(tool_call)
            console.print_panel(pretty)

            run_tool = await self.prompt_for_confirmation(f"Use {tool_call['name']}", True)

            if run_tool:
                tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            else:
                tool_result = {"result": "User declined tool call."}

                # Create constraint to avoid this tool with these specific arguments
                constraint = ConstraintSchema(
                    type="avoid",
                    description=f"Do not use {tool_call['name']} with arguments: {json.dumps(tool_call['args'])}",
                    source="declined_tool",
                )

                # Send back to assistant_node but remove the last message.
                return Command(
                    goto="assistant_node",
                    update={"scratch_messages": [RemoveMessage(id=message.id)], "constraints": [constraint]},
                )

            # Display tool result and confirm if it should be added to response
            result_pretty = Text(tool_result)
            console.print_panel(result_pretty, title="Tool Result")

            add_result = await self.prompt_for_confirmation("Add this result to the response?", True)

            if not add_result:
                tool_result = {"result": "User did not find the results useful for the task."}

            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return Command(goto="assistant_node", update={"scratch_messages": outputs})
