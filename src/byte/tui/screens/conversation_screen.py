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
from byte.tui.screens.usage_analytics_screen import UsageAnalyticsScreen
from byte.tui.widgets.bootbox import Bootbox
from byte.tui.widgets.conversation import Conversation

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ConversationScreen(Screen[None]):
    """Display and manage the conversation interface."""

    app: ByteTUI

    conversation = getters.query_one(Conversation)
    is_working = reactive(False, bindings=True)
    is_cancelling = reactive(False, bindings=True)

    DEFAULT_CSS = """
        ConversationScreen {
            Conversation {
                height: 1fr;
                overflow:hidden;
            }
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
        """Cancel the current workflow execution."""
        from byte.orchestration import WorkflowService

        self.is_cancelling = True
        self.conversation.post_message(Messages.Notify(content="Cancel requested - stopping after current step."))

        workflow_service = self.app.byte.make(WorkflowService)
        workflow_service.cancel()

    async def action_scroll_to_panel(self, panel_id: str) -> None:
        """Scroll to ensure the specified panel is visible."""
        await self.conversation.chat_container.ensure_panel_visible(panel_id)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Validate if an action is allowed to execute."""
        if action == "cancel_request":
            if self.is_cancelling:
                return None
            if not self.is_working:
                return False
        return True

    @on(Messages.CommandExecutionStarted)
    async def command_execution_started(self, event: Messages.CommandExecutionStarted) -> None:
        """Mark the workflow as executing."""
        self.is_working = True

    @on(Messages.CommandExecutionCompleted)
    async def command_execution_completed(self, event: Messages.CommandExecutionCompleted) -> None:
        """Mark the workflow as complete."""
        self.is_working = False
        self.is_cancelling = False

    def compose(self) -> ComposeResult:
        """Compose the screen layout with conversation widget and footer."""
        yield Conversation()
        yield Footer(show_command_palette=False)

    async def on_mount(self) -> None:
        """Initialize the screen with post-boot messages."""
        event_bus = self.app.byte.make(EventBus)

        # Emit our post boot message to gather all needed info.
        payload = await event_bus.emit(SystemEvents.PostBoot(messages=[]))
        messages = payload.messages

        response_chatbox = Bootbox(messages=messages)
        await self.conversation.chat_container.mount(response_chatbox)

    @work
    async def action_request_manage_files(self) -> None:
        """Display the manage files screen and refresh file statistics."""
        await self.app.push_screen_wait(ManageFilesScreen())
        file_service = self.app.byte.make(FileService)
        await file_service.notify_file_stats()

    @work
    async def action_request_manage_context(self) -> None:
        """Display the manage context screen and refresh context statistics."""
        await self.app.push_screen_wait(ManageContextScreen())
        session_context_service = self.app.byte.make(SessionContextService)
        session_context_service.notify_context_stats()

    @work
    async def action_request_usage_analytics(self) -> None:
        """Display the usage analytics screen."""
        await self.app.push_screen_wait(UsageAnalyticsScreen())
