from typing import TYPE_CHECKING, ClassVar

from textual import getters, on, work
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer

from byte import EventBus
from byte.files import FileService
from byte.knowledge import SessionContextService
from byte.system import SystemEvents
from byte.tui import Messages
from byte.tui.screens.manage_context_screen import ManageContextScreen
from byte.tui.screens.manage_files_screen import ManageFilesScreen
from byte.tui.widgets.bootbox import Bootbox
from byte.tui.widgets.conversation import Conversation

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ConversationScreen(Screen[None]):
    app: ByteTUI

    conversation = getters.query_one(Conversation)
    is_working = reactive(False, bindings=True)

    DEFAULT_CSS = """
        ConversationScreen {

        }
        """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            key="ctrl+z",
            action="cancel_request",
            description="Cancel",
            show=True,
            priority=True,
        ),
    ]

    def action_cancel_request(self) -> None:
        from byte.workflow import WorkflowService

        workflow_service = self.app.byte.make(WorkflowService)
        workflow_service.cancel()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        self.app.byte["log"].info(action)
        if action == "cancel_request":
            if not self.is_working:
                return False
        return True

    @on(Messages.CommandExecutionStarted)
    async def command_execution_started(self, event: Messages.CommandExecutionStarted) -> None:
        self.is_working = True

    @on(Messages.CommandExecutionCompleted)
    async def command_execution_completed(self, event: Messages.CommandExecutionCompleted) -> None:
        self.is_working = False

    def compose(self) -> ComposeResult:
        yield Conversation()
        yield Footer(show_command_palette=False)

    async def on_mount(self):

        # TODO: This should not be here I think.
        event_bus = self.app.byte.make(EventBus)

        # Emit our post boot message to gather all needed info.
        payload = await event_bus.emit(SystemEvents.PostBoot(messages=[]))
        messages = payload.messages

        styled_logo = []
        logo_lines = [
            "░       ░░░  ░░░░  ░░        ░░        ░",
            "▒  ▒▒▒▒  ▒▒▒  ▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒",
            "▓       ▓▓▓▓▓    ▓▓▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓",
            "█  ████  █████  ████████  █████  ███████",
            "█       ██████  ████████  █████        █",
        ]

        for row_idx, line in enumerate(logo_lines):
            styled_line = ""
            for col_idx, char in enumerate(line):
                # Calculate diagonal position (0.0 = top-left, 1.0 = bottom-right)
                diagonal_progress = (row_idx + col_idx) / (len(logo_lines) + len(line) - 2)

                # Use primary for first half, secondary for second half of diagonal
                if diagonal_progress < 0.5:
                    styled_line += f"[$primary]{char}[/$primary]"
                else:
                    styled_line += f"[$secondary]{char}[/$secondary]"

            # Fill remaining width with the last character
            logo_width = len(line)
            remaining_width = self.size.width - logo_width - 20

            if remaining_width > 0:
                last_char = line[-1] if line else " "
                last_diagonal_progress = (row_idx + len(line) - 1) / (len(logo_lines) + len(line) - 2)
                style = "$primary" if last_diagonal_progress < 0.5 else "$secondary"
                styled_line += f"[{style}]{last_char * remaining_width}[/{style}]"

            styled_logo.append(styled_line)

        response_chatbox = Bootbox("\n".join(styled_logo) + "\n\n" + "\n".join(messages))
        self.conversation.chat_container.mount(response_chatbox)

    @work
    async def action_request_manage_files(self) -> None:
        """"""
        await self.app.push_screen_wait(ManageFilesScreen())
        file_service = self.app.byte.make(FileService)
        await file_service.notify_file_stats()

    @work
    async def action_request_manage_context(self) -> None:
        """"""
        await self.app.push_screen_wait(ManageContextScreen())
        session_context_service = self.app.byte.make(SessionContextService)
        session_context_service.notify_context_stats()
