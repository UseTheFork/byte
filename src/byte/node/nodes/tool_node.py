from langgraph.types import Command

from byte.node import BaseNode
from byte.orchestration import BaseState
from byte.support.utils import get_last_message
from byte.tools import ToolMessage, ToolRegistryService
from byte.tools.exceptions import ToolException, ToolNotFoundException
from byte.tools.schemas import ToolResult
from byte.tui import Messages


class ToolNode(BaseNode):
    def boot(
        self,
        **kwargs,
    ):
        self.tool_registry_service = self.app.make(ToolRegistryService)

    def _update_tui(self, tool_message: ToolMessage, tool_result: ToolResult | None = None) -> None:

        tool = self.tool_registry_service.get_tool(str(tool_message.name))

        content = tool.format_tui_message(tool_result) if tool and tool_result else str(tool_message.text)

        self.emit_tui(
            Messages.ToolCall(
                tool_id=str(tool_message.tool_call_id),
                status=tool_message.status,
                content=content,
            )
        )

    async def __call__(
        self,
        state: BaseState,
    ) -> Command[str]:
        message = get_last_message(state["scratch_messages"])

        outputs = []
        merged_extra = {}

        # TODO: we should make this truly async with a gather

        for tool_call in message.tool_calls:
            try:
                tool = self.tool_registry_service.get_tool(tool_call["name"])
                if not tool:
                    raise ToolNotFoundException(
                        f"Error: Tool '{tool_call['name']}' is not available or does not exist."
                    )

                tool_result = await tool.invoke(
                    args=tool_call["args"],
                    state=state,
                    tool_call_id=tool_call["id"],
                )

                tool_message = ToolMessage(
                    content=tool.format_tool_message(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )

                # TODO: This prob needs to have a deep merge.
                if tool_result.extra:
                    merged_extra.update(tool_result.extra)

                self._update_tui(tool_message, tool_result)
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

        update = {"scratch_messages": outputs, **merged_extra}

        # Final single route_back after ALL tools
        if any(tc["name"] == "complete_turn" for tc in message.tool_calls):
            return self.route_to("end_node", update)

        return self.route_back(state, update)
