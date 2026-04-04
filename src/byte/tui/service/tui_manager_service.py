from byte import CommandRegistryService, Events
from byte.support import Service
from byte.tui import ByteTUI, Messages


class TUIManagerService(Service):
    """ """

    # Manages the Textual TUI entrypoint etc.

    def boot(self) -> None:
        """Initialize the chatbox manager with empty state.

        Usage: Called automatically during service container boot process
        """
        self.tui = ByteTUI(container=self.app)
        self.command_registry = self.app.make(CommandRegistryService)
        self.current_agent_panel = None

    async def run_async(self):
        await self.tui.run_async()

    async def _create_pending_response_panel(self):
        self.current_agent_panel = await self.tui.mount_pending_response_panel()
        self.tui.chat_container.refresh(layout=True)

    async def _update_pending_response_header(self, event: Messages.AgentResponseStarted):
        assert self.current_agent_panel

        self.current_agent_panel.heading.toggle_class("hidden")
        self.current_agent_panel.heading.text = event.agent
        self.tui.chat_container.refresh(layout=True)

    async def _handle_ai_message_chunk(self, event: Messages.AIMessageChunk):
        # TODO: need to assert here.
        assert self.current_agent_panel

        self.current_agent_panel.rune_spinner.display = "none"
        self.current_agent_panel.agent_response_widget.update(event.chunk)
        self.tui.conversation.scroll_to_latest_message()
        # current_chatbox.agent_response_widget.update(self.current_chatbox.response)

    async def route_message(self, event: Events.TuiMessage):
        if isinstance(event.message, Messages.WorkflowStarted):
            await self._create_pending_response_panel()
        elif isinstance(event.message, Messages.AgentResponseStarted):
            await self._update_pending_response_header(event.message)
        elif isinstance(event.message, Messages.AIMessageChunk):
            await self._handle_ai_message_chunk(event.message)

        # # TODO: We need a fallback on to coder command here.

    async def _handle_command_input(self, user_input: str):
        """Parse and execute slash commands.

        Args:
                user_input: Raw user input starting with /

        Usage: Called internally when user input starts with /
        """
        # Parse command name and args
        parts = user_input[1:].split(" ", 1)  # Remove "/" and split
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # console = self.app["console"]

        # Get command registry and execute
        command_registry = self.app.make(CommandRegistryService)
        command = command_registry.get_slash_command(command_name)

        if command:
            await command.handle(args)
        else:
            pass
            # TODO: This should flash an error
            # console.print_error(f"Unknown command: /{command_name}")

    async def handle_user_message(self, event: Events.UserInputSubmitted):
        user_input = event.message
        if user_input.startswith("/"):
            await self._handle_command_input(event.message)
