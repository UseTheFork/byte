from __future__ import annotations

from typing import TYPE_CHECKING

from langchain.messages import AIMessageChunk
from textual import getters, on, work
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.reactive import reactive
from textual.widgets import Markdown

from byte import Command
from byte.support.utils import extract_content_from_message
from byte.tui import Messages
from byte.tui.widgets.rune_spinner import RuneSpinner

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class AgentResponsePanel(VerticalGroup):
    BINDINGS = []

    DEFAULT_CSS = """\
    AgentResponsePanel {
        height: auto;
        width: 1fr;
        min-height: 1;
        min-width: 12;
        max-width: 1fr;
        margin: 0 1;
        border: round $secondary 60%;
    }
    """

    app: ByteTUI

    rune_spinner = getters.query_one("#rune_spinner", RuneSpinner)
    agent_response_widget = getters.query_one("#agent_response", Markdown)

    response = reactive("", init=False)

    def __init__(
        self,
        command: Command,
        request: str,
        args: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.command = command
        self.request = request
        self.args = args

    @work(exclusive=True)
    async def _execute_command(self) -> None:
        """Execute the command and handle streaming."""
        # try:
        # Commands should emit streaming events that we listen to
        await self.command.handle(
            self.args,
            event_handler=self.event_handler,
        )

    async def on_mount(self) -> None:
        """Start command execution when panel is mounted."""
        # Emit start event
        # self.post_message(Messages.CommandExecutionStarted(command_name=self.command.name))

        # Execute command
        self._execute_command()

        # self.post_message(Messages.CommandExecutionComplete(panel_id=self.name, success=True))
        # except Exception as e:
        # self.post_message(Messages.CommandExecutionComplete(panel_id=self.name, success=False, result=str(e)))

    async def event_handler(self, event) -> None:
        """Handle and dispatch events for this panel."""
        self.post_message(event)

    @on(Messages.CommandStreamChunk)
    async def handle_stream_chunk(self, event: Messages.CommandStreamChunk) -> None:
        """Handle streaming chunks for this panel."""

        # Update UI based on chunk type
        if event.chunk["type"] == "messages":
            message_chunk, metadata = event.chunk["data"]

            if isinstance(message_chunk, AIMessageChunk) and message_chunk.content:
                self.rune_spinner.display = "none"

                msg = extract_content_from_message(message_chunk)
                self.app.byte["log"].info(msg)
                self.response += msg
                self.agent_response_widget.update(self.response)
                self.app.conversation.scroll_to_latest_message()

        elif event.chunk["type"] == "tasks":
            # await self._update_task_status(event.data)
            self.app.byte["log"].info(event.chunk)

    def compose(self) -> ComposeResult:
        yield RuneSpinner(id="rune_spinner")
        yield Markdown(id="agent_response")
