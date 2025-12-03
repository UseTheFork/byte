from typing import AsyncGenerator

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Group

from byte.core.config.config import ByteConfg
from byte.core.event_bus import EventType, Payload
from byte.core.logging import log
from byte.core.service.base_service import Service
from byte.domain.agent.implementations.subprocess.agent import SubprocessAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.service.command_registry import CommandRegistry
from byte.domain.cli.service.console_service import ConsoleService


class CommandCompleter(Completer):
    """Async completer for slash commands and their arguments.

    Provides intelligent autocomplete for commands registered in the
    CommandRegistry, supporting both command names and their arguments.
    Usage: Automatically used by PromptSession for command completion
    """

    def __init__(self):
        self.command_registry = None

    def get_completions(self, document: Document, complete_event):
        """Synchronous completion method (unused - see get_completions_async).

        Required by Completer interface but not used since we implement async version.
        """
        pass

    async def get_completions_async(self, document: Document, complete_event) -> AsyncGenerator[Completion, None]:
        """Async generator for completions using the InputActor."""

        if not self.command_registry:
            from byte.context import make

            self.command_registry = await make(CommandRegistry)

        text = document.text_before_cursor

        if text.startswith("/"):
            completions = await self.command_registry.get_slash_completions(text)

            # Parse to determine what part to replace
            if " " in text:
                _, args_part = text.split(" ", 1)
                # Replace only the args part
                for completion in completions:
                    yield Completion(completion, start_position=-len(args_part))
            else:
                # Replace the command part (minus the /)
                cmd_prefix = text[1:]
                for completion in completions:
                    yield Completion(completion, start_position=-len(cmd_prefix))


class PromptToolkitService(Service):
    """Service for handling interactive user input via prompt_toolkit.

    Manages the prompt session with history, command completion, and interrupt
    handling. Coordinates with the event bus to allow other domains to modify
    prompt behavior and handle user input.
    Usage: `await prompt_service.execute()` -> displays prompt and processes input
    """

    async def boot(self):
        """Initialize the prompt session with history and completion support."""
        # Placeholder for `prompt_async` if we where interupted we restore using the placeholder
        self.placeholder = None
        self.interrupted = False

        self.completer = CommandCompleter()

        config = await self.make(ByteConfg)

        self.prompt_session = PromptSession(
            history=FileHistory(config.byte_cache_dir / ".input_history"),
            multiline=False,
            completer=self.completer,
        )

    async def execute(self):
        """Display prompt, capture user input, and route to appropriate handler.

        Emits PRE_PROMPT_TOOLKIT and POST_PROMPT_TOOLKIT events to allow other
        domains to customize prompt behavior. Routes input to command handler
        for slash commands or agent execution for natural language input.

        Usage: Called by main loop to handle each user interaction
        """
        console = await self.make(ConsoleService)

        # Use placeholder if set, then clear it
        default = self.placeholder or ""
        self.placeholder = None
        self.interrupted = False

        message = "> "

        # Create payload with event type
        payload = Payload(
            event_type=EventType.PRE_PROMPT_TOOLKIT,
            data={
                "placeholder": self.placeholder,
                "interrupted": self.interrupted,
                "message": message,
                "info_panel": [],
            },
        )

        # Send the payload event and wait for systems to return as needed
        payload = await self.emit(payload)
        info_panel = payload.get("info_panel", [])
        message = payload.get("message", message)

        console.print()
        console.rule("[primary]/[/primary][secondary]/[/secondary] Byte")
        # Output info panel if it contains content
        if info_panel:
            console.print(Group(*info_panel))

        try:
            user_input = await self.prompt_session.prompt_async(message=message, default=default)
        except KeyboardInterrupt:
            # Ask for confirmation before quitting
            console.print()  # Add newline after ^C
            should_quit = console.confirm("Do you want to quit?", default=True)

            if should_quit:
                # User confirmed quit - raise to exit the application
                raise
            else:
                # User wants to continue - return without processing input
                return

        console.print()
        # TODO: should we make `user_input` a [("user", user_input)], in this situation.

        agent_service = await self.make(AgentService)
        active_agent = agent_service.get_active_agent()

        payload = Payload(
            event_type=EventType.POST_PROMPT_TOOLKIT,
            data={
                "user_input": user_input,
                "interrupted": self.interrupted,
                "active_agent": active_agent,
            },
        )
        payload = await self.emit(payload)

        interrupted = payload.get("interrupted", self.interrupted)
        user_input = payload.get("user_input", user_input)
        active_agent = payload.get("active_agent", active_agent)

        if not interrupted:
            if user_input.startswith("/"):
                await self._handle_command_input(user_input)
            elif user_input.startswith("!"):
                await self._handle_subcommand_input(user_input)
            else:
                # Only execute agent if user provided non-empty input
                if user_input.strip():
                    await agent_service.execute_agent(user_input, active_agent)

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

        console = await self.make(ConsoleService)

        # Get command registry and execute
        command_registry = await self.make(CommandRegistry)
        command = command_registry.get_slash_command(command_name)

        if command:
            try:
                await command.handle(args)
            except Exception as e:
                log.exception("Oops")
                console.print_error_panel(f"{e}", title="Oops")
        else:
            console.print_error(f"Unknown command: /{command_name}")

    async def _handle_subcommand_input(self, user_input: str):
        """Parse and execute subcommands starting with !.

        Args:
                user_input: Raw user input starting with !

        Usage: Called internally when user input starts with !
        """

        user_input = user_input[1:]

        subprocess_agent = await self.make(SubprocessAgent)
        await subprocess_agent.execute(user_input, display_mode="silent")
        # TODO: Should we execute somthing after this?

    async def interrupt(self):
        """Interrupt the current prompt and preserve user input.

        Stores the current buffer text in placeholder for restoration on next
        prompt. Used for handling interrupts like agent execution starting.

        Usage: Called by other services to interrupt the prompt gracefully
        """
        try:
            if self.prompt_session and self.prompt_session.app:
                self.placeholder = self.prompt_session.app.current_buffer.text
                self.interrupted = True
                self.prompt_session.app.exit()
        except Exception:
            pass

    def is_interrupted(self) -> bool:
        """Check if the current prompt has been interrupted.

        Returns True if interrupt() was called and the prompt was interrupted,
        False otherwise. Useful for other services to check interrupt state.

        Usage: `if await prompt_service.is_interrupted(): ...`
        """
        return self.interrupted

    def set_placeholder(self, text: str) -> None:
        """Set the placeholder text for the next prompt.

        The placeholder text will be pre-filled in the input buffer when the
        next prompt is displayed, allowing users to edit or submit it directly.

        Args:
            text: The text to pre-fill in the next prompt

        Usage: `prompt_service.set_placeholder("some default text")`
        """
        self.placeholder = text
