from typing import Literal

from langchain.messages import AIMessage, HumanMessage
from langgraph.graph import END
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.clipboard import ClipboardService
from byte.node import Node, NodeEvents
from byte.orchestration import AssistantContextSchema, BaseState
from byte.support import Boundary, BoundaryType
from byte.support.utils import get_last_ai_message, list_to_multiline_text


class EndNode(Node):
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

        if state["parsed_blocks"]:
            if runtime.context.agent == "CoderAgent":
                clipboard_service = self.app.make(ClipboardService)
                self.app.dispatch_task(clipboard_service.extract_from_blocks(state["parsed_blocks"]))

        # This is where we promote `scratch_messages` to `history_messages`
        update_dict = {
            **state,
            # We always want to erase the current user request
            "user_request": "",
        }

        metadata = state["metadata"]

        agent = state.get("agent", "")

        # Only update messages if there are scratch messages to process
        if state["scratch_messages"] and not metadata.erase_history:
            last_message = get_last_ai_message(state["scratch_messages"])
            update_dict["final_message"] = last_message

            # we only need to copy from Ask and Coder agents.
            if agent == "AskAgent":
                clipboard_service = self.app.make(ClipboardService)
                self.app.dispatch_task(clipboard_service.extract_from_message(last_message))

            # For SubprocessAgent, skip adding user_message since the command is already in context
            # TODO: this is gross we need a better way of doing this. maybe a hook that is part of the runtime?
            if agent == "SubprocessAgent":
                update_dict["history_messages"] = [last_message]
            else:
                # Extract text content from message (handles both list and string formats)
                content_text = self._extract_text_from_content(last_message.content)

                # Wrap the message in XML for parsing later.
                last_message = list_to_multiline_text(
                    [
                        Boundary.open(BoundaryType.AGENT_MESSAGE, {"agent_type": agent}),
                        str(content_text),
                        Boundary.close(BoundaryType.AGENT_MESSAGE),
                    ]
                )
                last_message = AIMessage(content=last_message)

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
            goto=END,
            update=update_dict,
        )
