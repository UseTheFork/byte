from typing import Literal

from langchain.messages import HumanMessage, RemoveMessage
from langgraph.graph import END
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte import EventType, Payload
from byte.agent import AssistantContextSchema, BaseState, Node
from byte.clipboard import ClipboardService
from byte.support.utils import get_last_message


class EndNode(Node):
    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["__end__"]]:
        if runtime is not None and runtime.context is not None:
            payload = Payload(
                event_type=EventType.END_NODE,
                data={
                    "state": state,
                    "agent": runtime.context.agent,
                },
            )
            await self.emit(payload)

        # This is where we promote `scratch_messages` to `history_messages`
        update_dict = {
            **state,
            # We always want to erase the current user request
            "user_request": "",
        }

        # Only update messages if there are scratch messages to process
        if state["parsed_blocks"]:
            if runtime.context.agent == "CoderAgent":
                clipboard_service = self.app.make(ClipboardService)
                self.app.dispatch_task(clipboard_service.extract_from_blocks(state["parsed_blocks"]))

        if state["scratch_messages"]:
            last_message = get_last_message(state["scratch_messages"])
            clear_scratch = RemoveMessage(id=REMOVE_ALL_MESSAGES)

            # we only need to copy from Ask and Coder agents.
            if runtime.context.agent == "AskAgent":
                clipboard_service = self.app.make(ClipboardService)
                self.app.dispatch_task(clipboard_service.extract_from_message(last_message))

            # For SubprocessAgent, skip adding user_message since the command is already in context
            # TODO: this is gross we need a better way of doing this. maybe a hook that is part of the runtime?
            if runtime.context.agent == "SubprocessAgent":
                update_dict["history_messages"] = [last_message]
            else:
                # Create a HumanMessage from the user_request
                user_message = HumanMessage(content=state["user_request"])
                update_dict["history_messages"] = [user_message, last_message]

            update_dict["scratch_messages"] = clear_scratch

        return Command(
            goto=END,
            update=update_dict,
        )
