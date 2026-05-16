from typing import Literal

from langchain.messages import HumanMessage, ToolMessage
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.node import BaseNode, NodeEvents
from byte.orchestration import AssistantContextSchema, BaseState, CompleteSimpleTurnTool, CompleteTurnTool
from byte.orchestration.messages import AIMessage
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text


class EndNode(BaseNode):
    """Finalize agent execution by promoting scratch messages to history and emitting end events.

    Usage: Automatically invoked by LangGraph when agent workflow completes.
    Handles message promotion, clipboard extraction, and state cleanup.
    """

    def _generate_final_message(self, scratch_messages: list) -> str:
        """Generate a final message from the complete_turn tool message."""
        last_ai_message = next((m for m in reversed(scratch_messages) if isinstance(m, AIMessage)), None)
        agent_name = last_ai_message.agent_name if last_ai_message else "unknown"

        complete_turn_message = next(
            (
                m
                for m in reversed(scratch_messages)
                if isinstance(m, ToolMessage)
                and m.name
                in [
                    CompleteTurnTool.name,
                    CompleteSimpleTurnTool.name,
                ]
            ),
            None,
        )

        if complete_turn_message:
            content_text = complete_turn_message.text

            return list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.AGENT_MESSAGE, meta={"agent_type": agent_name}),
                    content_text,
                    Boundary.close(BoundaryType.AGENT_MESSAGE),
                ]
            )

        message_parts = []

        for message in scratch_messages:
            if isinstance(message, AIMessage):
                # Extract text content from AIMessage
                content_text = message.text

                if not message.mask:
                    content_text = list_to_multiline_text(
                        [
                            Boundary.open(BoundaryType.AGENT_MESSAGE, meta={"agent_type": message.agent_name}),
                            content_text,
                            Boundary.close(BoundaryType.AGENT_MESSAGE),
                        ]
                    )

                message_parts.append(content_text)
            # elif isinstance(message, ToolMessage):
            #     # Add tool execution summary
            #     tool_name = getattr(message, "name", "unknown tool")
            #     tool_status = getattr(message, "status", "unknown")
            #     content_text = list_to_multiline_text(
            #         [
            #             Boundary.open(BoundaryType.TOOL_CALL),
            #             f"Called {tool_name} applied with status {tool_status}",
            #             Boundary.close(BoundaryType.TOOL_CALL),
            #         ]
            #     )

        return list_to_multiline_text(message_parts)

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["__end__"]]:
        if runtime is not None and runtime.context is not None:
            await self.emit(
                NodeEvents.EndNode(
                    state=state,
                    agent=runtime.context.agent,
                )
            )

        # This is where we promote `scratch_messages` to `history_messages`
        update_dict = {
            **state,
            # Clear the plan assuming its been completed.
            "plan": [],
            # We always want to erase the current user request
            "user_request": "",
        }

        metadata = state["metadata"]

        # agent = state.get("agent", "")

        # TODO: This will need to become a combined state with out the tool calls.
        # Only update messages if there are scratch messages to process
        if state["scratch_messages"] and not metadata.erase_history and not state["is_cancelled"]:
            generated_final_message = self._generate_final_message(state["scratch_messages"])
            last_message = AIMessage(content=generated_final_message)
            update_dict["final_message"] = generated_final_message

            # Create a HumanMessage from the user_request
            user_message = list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.USER_MESSAGE),
                    str(state["user_request"]),
                    Boundary.close(BoundaryType.USER_MESSAGE),
                ]
            )
            user_message = HumanMessage(content=user_message)

            update_dict["history_messages"] = [user_message, last_message]

        return Command(
            goto="__end__",
            update=update_dict,
        )
