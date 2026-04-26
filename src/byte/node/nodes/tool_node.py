import json

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import ValidationError

from byte.node import BaseNode
from byte.orchestration import AssistantContextSchema, BaseState
from byte.support.utils import get_last_message
from byte.tools import ToolMessage, ToolRegistryService, ToolResult
from byte.tui import Messages


class ToolNode(BaseNode):
    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[str]:
        message = get_last_message(state["scratch_messages"])

        outputs = []
        merged_extra = {}

        tool_registry_service = self.app.make(ToolRegistryService)
        tools = tool_registry_service.get_all_tools()

        # Check if tools are available
        if not tools:
            return self.route_back(state, {"scratch_messages": []})

        # Build a mapping of tool names to tool instances
        tools_by_name = {tool.name: tool for tool in tools}

        for tool_call in message.tool_calls:
            if tool_call["name"] not in tools_by_name:
                tool_message = ToolMessage(
                    status="error",
                    content=f"Error: Tool '{tool_call['name']}' is not available or does not exist.",
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )

                self._update_tui(tool_message)
                outputs.append(tool_message)
                continue

            try:
                tool_result = await tools_by_name[tool_call["name"]].ainvoke(
                    {
                        **tool_call["args"],
                        "app": self.app,
                    },
                )
            except ValidationError as err:
                tool_message = ToolMessage(
                    status="error",
                    content=f"Error: Input validation Failed {err}",
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )

                self._update_tui(tool_message)
                outputs.append(tool_message)
                continue

            # Handle ToolResult wrapper
            if isinstance(tool_result, ToolResult):
                tool_message = ToolMessage(
                    content=json.dumps(tool_result.result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )

                self._update_tui(tool_message)
                outputs.append(tool_message)

                # TODO: This prob needs to have a deep merge.
                if tool_result.extra:
                    # merge extras
                    merged_extra.update(tool_result.extra)

            else:
                tool_message = ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
                self._update_tui(tool_message)
                outputs.append(tool_message)

        # Final single route_back after ALL tools
        return self.route_back(
            state,
            {
                "scratch_messages": outputs,
                **merged_extra,  # only included if not empty
            },
        )

    def _update_tui(self, tool_message: ToolMessage) -> None:
        self.emit_tui(
            Messages.ToolCall(
                tool_id=str(tool_message.id),
                status=tool_message.status,
                content=str(tool_message.content),
            )
        )
