from __future__ import annotations

import datetime
from typing import Literal, cast

from langchain.messages import HumanMessage
from langchain_core.messages import AIMessage
from textual import events, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from byte import Application
from byte.tui import Messages
from byte.tui.schemas import ChatMessage
from byte.tui.widgets.chatbox import Chatbox
from byte.tui.widgets.flash import Flash
from byte.tui.widgets.prompt import Prompt

# if TYPE_CHECKING:


class Conversation(Widget):
    BINDING_GROUP_TITLE = "Conversation"

    BINDINGS = [
        Binding("ctrl+r", "rename", "Rename", key_display="^r"),
        Binding("shift+down", "scroll_container_down", show=False),
        Binding("shift+up", "scroll_container_up", show=False),
        Binding(
            key="g",
            action="focus_first_message",
            description="First message",
            key_display="g",
            show=False,
        ),
        Binding(
            key="G",
            action="focus_latest_message",
            description="Latest message",
            show=False,
        ),
        Binding(key="f2", action="details", description="Chat info"),
    ]

    allow_input_submit = reactive(True)

    def __init__(
        self,
        # chat_data: ChatData,
    ) -> None:
        super().__init__()
        self.chat_data = []
        self.byte_app = cast(Application, self.app.byte)  # ty:ignore[possibly-missing-attribute]

    """Used to lock the chat input while the agent is responding."""

    def compose(self) -> ComposeResult:
        # yield ResponseStatus()
        # yield ChatHeader("123", "test")

        with VerticalScroll(id="chat-container") as vertical_scroll:
            vertical_scroll.can_focus = False

        yield Prompt(id="prompt")

    async def on_mount(self, _: events.Mount) -> None:
        """
        When the component is mounted, we need to check if there is a new chat to start
        """
        # Register container with chatbox manager
        from byte.tui import TUIManagerService

        chatbox_manager = self.byte_app.make(TUIManagerService)
        chatbox_manager.register_container(self.chat_container)

    @property
    def chat_container(self) -> VerticalScroll:
        return self.query_one("#chat-container", VerticalScroll)

    @on(Messages.Flash)
    def on_flash(self, event: Messages.Flash) -> None:
        event.stop()
        self.flash(event.content, duration=event.duration, style=event.style)

    def flash(
        self,
        content: str | Content,
        *,
        duration: float | None = None,
        style: Literal["default", "warning", "error", "success"] = "default",
    ) -> None:
        """Flash a single-line message to the user.

        Args:
            content: Content to flash.
            style: A semantic style.
            duration: Duration in seconds of the flash, or `None` to use default in settings.
        """
        self.query_one(Flash).flash(content, duration=duration, style=style)

    def scroll_to_latest_message(self):
        container = self.chat_container
        container.refresh()
        container.scroll_end(animate=False, force=True)

    @on(Messages.AgentResponseFailed)
    def restore_state_on_agent_failure(self, event: Messages.AgentResponseFailed) -> None:
        original_prompt = event.last_message.message.content
        if isinstance(original_prompt, str):
            self.query_one(Prompt).text = original_prompt

    async def new_user_message(self, content: str) -> None:
        now_utc = datetime.datetime.now(datetime.UTC)
        user_message = HumanMessage(content)

        user_chat_message = ChatMessage(user_message, now_utc)
        # self.chat_data.messages.append(user_chat_message)
        user_message_chatbox = Chatbox(user_chat_message)

        assert self.chat_container is not None, "Textual has mounted container at this point in the lifecycle."

        await self.chat_container.mount(user_message_chatbox)

        self.scroll_to_latest_message()
        self.post_message(Messages.NewUserMessage(content))

        # await ChatsManager.add_message_to_chat(chat_id=self.chat_data.id, message=user_chat_message)

        self.post_message(Messages.AgentResponseStarted())

        prompt = self.query_one(Prompt)
        # prompt.submit_ready = False
        self.stream_agent_response()

    @work(thread=True, group="agent_response")
    async def stream_agent_response(self) -> None:
        # make call here.

        # ai_message: ChatCompletionAssistantMessageParam = {
        #     "content": "",
        #     "role": "assistant",
        # }
        now = datetime.datetime.now(datetime.UTC)

        message = ChatMessage(message=AIMessage("test"), timestamp=now)
        response_chatbox = Chatbox(
            message=message,
            classes="response-in-progress",
        )
        # self.post_message(self.AgentResponseStarted())
        self.app.call_from_thread(self.chat_container.mount, response_chatbox)

        # assert self.chat_container is not None, "Textual has mounted container at this point in the lifecycle."

        # try:
        #     chunk_count = 0
        #     async for chunk in response:
        #         chunk = cast(ModelResponse, chunk)
        #         response_chatbox.border_title = "Agent is responding..."

        #         chunk_content = chunk.choices[0].delta.content
        #         if isinstance(chunk_content, str):
        #             self.app.call_from_thread(response_chatbox.append_chunk, chunk_content)
        #         else:
        #             break

        #         scroll_y = self.chat_container.scroll_y
        #         max_scroll_y = self.chat_container.max_scroll_y
        #         if scroll_y in range(max_scroll_y - 3, max_scroll_y + 1):
        #             self.app.call_from_thread(self.chat_container.scroll_end, animate=False)

        #         chunk_count += 1
        # except Exception:
        #     self.notify(
        #         "There was a problem using this model. Please check your configuration file.",
        #         title="Error",
        #         severity="error",
        #         timeout=constants.ERROR_NOTIFY_TIMEOUT_SECS,
        #     )
        #     self.post_message(self.AgentResponseFailed(self.chat_data.messages[-1]))
        # else:
        self.post_message(
            Messages.AgentResponseComplete(
                chat_id=123,
                message=response_chatbox.message,
                chatbox=response_chatbox,
            )
        )

    @on(Messages.AgentResponseFailed)
    @on(Messages.AgentResponseStarted)
    async def agent_started_responding(
        self, event: Messages.AgentResponseFailed | Messages.AgentResponseStarted
    ) -> None:
        try:
            awaiting_reply = self.chat_container.query_one("#awaiting-reply", Label)
        except NoMatches:
            pass
        else:
            if awaiting_reply:
                await awaiting_reply.remove()

    @on(Messages.AgentResponseComplete)
    def agent_finished_responding(self, event: Messages.AgentResponseComplete) -> None:
        # Ensure the thread is updated with the message from the agent
        # self.chat_data.messages.append(event.message)
        event.chatbox.border_title = "Agent"
        event.chatbox.remove_class("response-in-progress")
        prompt = self.query_one(Prompt)
        # prompt.submit_ready = True

    @on(Prompt.CursorEscapingTop)
    async def on_cursor_up_from_prompt(self, event: Prompt.CursorEscapingTop) -> None:
        self.focus_latest_message()

    @on(Chatbox.CursorEscapingBottom)
    def move_focus_to_prompt(self) -> None:
        self.query_one(Prompt).focus()

    def get_latest_chatbox(self) -> Chatbox:
        return self.query(Chatbox).last()

    def focus_latest_message(self) -> None:
        try:
            self.get_latest_chatbox().focus()
        except NoMatches:
            pass

    def action_focus_latest_message(self) -> None:
        self.focus_latest_message()

    def action_focus_first_message(self) -> None:
        try:
            self.query(Chatbox).first().focus()
        except NoMatches:
            pass

    def action_scroll_container_up(self) -> None:
        if self.chat_container:
            self.chat_container.scroll_up()

    def action_scroll_container_down(self) -> None:
        if self.chat_container:
            self.chat_container.scroll_down()

    def action_close(self) -> None:
        self.app.clear_notifications()
        self.app.pop_screen()
