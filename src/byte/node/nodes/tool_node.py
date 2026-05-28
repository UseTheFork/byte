from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from byte.node import BaseNode
from byte.orchestration import BaseState, PhaseModel, PhaseUtils
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
        *,
        config: RunnableConfig,
    ) -> Command[str]:
        message = get_last_message(state["scratch_messages"])

        outputs = []
        workflow_phases = {}
        merged_extra = {}

        is_workflow_agent = PhaseUtils.is_workflow_agent(state)
        if is_workflow_agent:
            workflow_phases = state["workflow_phases"]
            current_phase = PhaseUtils.get_pending_phase(state)

        # TODO: we should make this truly async with a gather
        for tool_call in message.tool_calls:
            try:
                if is_workflow_agent and isinstance(current_phase, PhaseModel):
                    allowed_tool_names = [str(t.name) for t in current_phase.tools]
                    if tool_call["name"] not in allowed_tool_names:
                        raise ToolException(
                            f"Tool '{tool_call['name']}' is NOT allowed in the current phase. "
                            f"Allowed tools: {', '.join(allowed_tool_names) if allowed_tool_names else 'none'}"
                        )

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
                    content=[
                        {
                            "type": "text",
                            "text": tool.format_tool_message(tool_result),
                        }
                    ],
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )

                # TODO: This prob needs to have a deep merge.
                if tool_result.extra:
                    merged_extra.update(tool_result.extra)

                self._update_tui(tool_message, tool_result)
                outputs.append(tool_message)

                # If we are in a workflow we also need to update the state of the phase
                if is_workflow_agent:
                    workflow_phases = PhaseUtils.update_phase_with_tool_args(tool_call, workflow_phases)  # ty:ignore[invalid-argument-type]
            except ToolException as err:
                tool_message = ToolMessage(
                    status="error",
                    content=[
                        {
                            "type": "text",
                            "text": str(err),
                        }
                    ],
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
                self._update_tui(tool_message)
                outputs.append(tool_message)

        update = {"scratch_messages": outputs, "workflow_phases": workflow_phases, **merged_extra}

        # Final single route_back after ALL tools
        # TODO: This should prob move to routing.
        if any(
            (tool := self.tool_registry_service.get_tool(tc["name"])) and tool.terminates_turn
            for tc in message.tool_calls
        ):
            return self.route_to("end_node", update)

        return self.route_back(state, update)
