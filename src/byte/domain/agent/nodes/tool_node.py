import json

from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from rich.pretty import Pretty

from byte.core.mixins.user_interactive import UserInteractive
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.cli.service.console_service import ConsoleService


class ToolNode(Node, UserInteractive):
	async def __call__(self, inputs, runtime: Runtime[AssistantContextSchema]):
		if messages := inputs.get("messages", []):
			message = messages[-1]
		else:
			raise ValueError("No message found in input")
		outputs = []

		tools = runtime.context.tools
		# Build a mapping of tool names to tool instances
		tools_by_name = {tool.name: tool for tool in tools}

		for tool_call in message.tool_calls:
			console = await self.make(ConsoleService)

			pretty = Pretty(tool_call)
			console.print(console.panel(pretty))

			run_tool = await self.prompt_for_confirmation(f"Use {tool_call['name']}", True)

			if run_tool:
				tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
			else:
				tool_result = {"result": "User declined tool call."}

			# Display tool result and confirm if it should be added to response
			result_pretty = Pretty(tool_result)
			console.print(console.panel(result_pretty, title="Tool Result"))

			add_result = await self.prompt_for_confirmation("Add this result to the response?", True)

			if not add_result:
				tool_result = {"result": "User declined tool call."}

			outputs.append(
				ToolMessage(
					content=json.dumps(tool_result),
					name=tool_call["name"],
					tool_call_id=tool_call["id"],
				)
			)

		# Tools always go back to the `assistant_node`
		return Command(goto="assistant_node", update={"messages": outputs})
