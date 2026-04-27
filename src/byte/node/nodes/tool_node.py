import json

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.node import BaseNode
from byte.orchestration import AssistantContextSchema, BaseState
from byte.support.utils import get_last_message
from byte.tools import ToolMessage, ToolRegistryService
from byte.tools.exceptions import ToolException, ToolNotFoundException
from byte.tui import Messages


class ToolNode(BaseNode):
    def _update_tui(self, tool_message: ToolMessage) -> None:
        self.emit_tui(
            Messages.ToolCall(
                tool_id=str(tool_message.tool_call_id),
                status=tool_message.status,
                content=str(tool_message.text),
            )
        )

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[str]:
        message = get_last_message(state["scratch_messages"])

        outputs = []
        merged_extra = {}

        tool_registry_service = self.app.make(ToolRegistryService)

        # Build a mapping of tool names to tool instances

        # TODO: we should make this truily async with a gather

        for tool_call in message.tool_calls:
            #
            try:
                tool = tool_registry_service.get_tool(tool_call["name"])
                if not tool:
                    raise ToolNotFoundException(
                        f"Error: Tool '{tool_call['name']}' is not available or does not exist."
                    )
                    continue

                tool_result = await tool.invoke(
                    args=tool_call["args"],
                    tool_call_id=tool_call["id"],
                )
                self.app["log"].info(tool_result)

                tool_message = ToolMessage(
                    content=json.dumps(tool_result.result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )

                # TODO: This prob needs to have a deep merge.
                if tool_result.extra:
                    merged_extra.update(tool_result.extra)

                self._update_tui(tool_message)
                outputs.append(tool_message)

            except ToolException as err:
                tool_message = ToolMessage(
                    status="error",
                    content=str(err),
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
