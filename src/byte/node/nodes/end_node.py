from typing import Literal

from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.node import BaseNode, NodeEvents
from byte.node.messages import BaseAIMessage
from byte.orchestration import AssistantContextSchema, BaseState
from byte.support import Boundary, BoundaryType
from byte.support.utils import get_last_ai_message, list_to_multiline_text


class EndNode(BaseNode):
    """Finalize agent execution by promoting scratch messages to history and emitting end events.

    Usage: Automatically invoked by LangGraph when agent workflow completes.
    Handles message promotion, clipboard extraction, and state cleanup.
    """

    def _extract_text_from_content(self, content) -> str:
        """Extract text content from message content that may be a list or string.

        Usage: `text = self._extract_text_from_content(message.content)`
        """
        if isinstance(content, list):
            # Extract text from list format: [{'text': '...', 'type': 'text', 'index': 0}]
            text_parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
            return "".join(text_parts)
        return str(content)

    def _generate_final_message(self, scratch_messages: list) -> str:
        """Generate a final message by combining AI and Tool messages from scratch_messages.

        For AIMessage: extract text content only
        For ToolMessage: add a summary like "called tool.name applied successfully"
        Combines all into a single final message.
        """
        message_parts = []

        for message in scratch_messages:
            if isinstance(message, BaseAIMessage):
                # Extract text content from AIMessage

                if not message.mask:
                    content_text = list_to_multiline_text(
                        [
                            Boundary.open(BoundaryType.AGENT_MESSAGE, meta={"agent_type": message.agent_name}),
                            message.text,
                            Boundary.close(BoundaryType.AGENT_MESSAGE),
                        ]
                    )

                message_parts.append(content_text)
            elif isinstance(message, ToolMessage):
                # Add tool execution summary
                tool_name = getattr(message, "name", "unknown tool")
                tool_status = getattr(message, "status", "unknown")
                content_text = list_to_multiline_text(
                    [
                        Boundary.open(BoundaryType.TOOL_CALL),
                        f"Called {tool_name} applied with status {tool_status}",
                        Boundary.close(BoundaryType.TOOL_CALL),
                    ]
                )

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
            # We always want to erase the current user request
            "user_request": "",
        }

        metadata = state["metadata"]

        # agent = state.get("agent", "")

        # TODO: This will need to become a combined state with out the tool calls.
        # Only update messages if there are scratch messages to process
        if state["scratch_messages"] and not metadata.erase_history and not state["is_cancelled"]:
            last_message = get_last_ai_message(state["scratch_messages"])
            update_dict["final_message"] = last_message

            generated_final_message = self._generate_final_message(state["scratch_messages"])
            last_message = AIMessage(content=generated_final_message)

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
