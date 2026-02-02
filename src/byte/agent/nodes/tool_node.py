import json
from typing import Literal

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import RemoveMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from rich.pretty import Pretty
from rich.text import Text

from byte.agent import AssistantContextSchema, AssistantNode, BaseState, ConstraintSchema, Node
from byte.cli import InputCancelledError
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

        for tool_call in message.tool_calls:
            console = self.app["console"]

            pretty = Pretty(tool_call)
            console.print_panel(pretty)

            try:
                run_tool = await self.prompt_for_confirmation(f"Use {tool_call['name']}", True)
            except InputCancelledError:
                run_tool = None

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
                    goto=Str.class_to_snake_case(AssistantNode),
                    update={"scratch_messages": [RemoveMessage(id=message.id)], "constraints": [constraint]},
                )

            # Display tool result and confirm if it should be added to response
            result_pretty = Text(tool_result)
            console.print_panel(result_pretty, title="Tool Result")

            try:
                add_result = await self.prompt_for_confirmation("Add this result to the response?", True)
            except InputCancelledError:
                add_result = None

            if not add_result:
                tool_result = {"result": "User did not find the results useful for the task."}

            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return Command(goto=Str.class_to_snake_case(AssistantNode), update={"scratch_messages": outputs})
