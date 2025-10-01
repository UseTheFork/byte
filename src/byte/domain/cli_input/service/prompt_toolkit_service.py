from typing import AsyncGenerator

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Console, Group
from rich.rule import Rule

from byte.core.config.config import BYTE_DIR
from byte.core.event_bus import EventType, Payload
from byte.core.service.base_service import Service
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli_input.service.command_registry import CommandRegistry


class CommandCompleter(Completer):
    def __init__(self):
        self.command_registry = None

    def get_completions(self, document: Document, complete_event):
        pass

    async def get_completions_async(
        self, document: Document, complete_event
    ) -> AsyncGenerator[Completion, None]:
        """Async generator for completions using the InputActor."""

        if not self.command_registry:
            from byte.context import make

            self.command_registry = await make(CommandRegistry)

        text = document.text_before_cursor

        if text.startswith("/"):
            completions = await self.command_registry.get_slash_completions(text)

            # Parse to determine what part to replace
            if " " in text:
                cmd_part, args_part = text.split(" ", 1)
                # Replace only the args part
                for completion in completions:
                    yield Completion(completion, start_position=-len(args_part))
            else:
                # Replace the command part (minus the /)
                cmd_prefix = text[1:]
                for completion in completions:
                    yield Completion(completion, start_position=-len(cmd_prefix))


class PromptToolkitService(Service):
    """ """

    async def boot(self):
        # Placeholder for `prompt_async` if we where interupted we restore using the placeholder
        self.placeholder = None
        self.interrupted = False

        self.completer = CommandCompleter()

        self.prompt_session = PromptSession(
            history=FileHistory(BYTE_DIR / ".input_history"),
            multiline=False,
            completer=self.completer,
        )

    async def execute(self):
        console = await self.make(Console)

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
        console.print(
            Rule(
                "[primary]/[/primary][secondary]/[/secondary] Byte",
                style="text",
                align="left",
                characters="─",
            )
        )
        # Output info panel if it contains content
        if info_panel:
            console.print(Group(*info_panel))

        user_input = await self.prompt_session.prompt_async(
            message=message, placeholder=default
        )
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

        # log.debug(payload)

        if not interrupted:
            if user_input.startswith("/"):
                await self._handle_command_input(user_input)
            else:
                await agent_service.execute_agent([("user", user_input)], active_agent)

    async def _handle_command_input(self, user_input: str):
        # Parse command name and args
        parts = user_input[1:].split(" ", 1)  # Remove "/" and split
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        console = await self.make(Console)

        # Get command registry and execute
        command_registry = await self.make(CommandRegistry)
        command = command_registry.get_slash_command(command_name)

        if command:
            await command.execute(args)
        else:
            console.print(f"[error]Unknown command: /{command_name}[/error]")

    async def interrupt(self):
        if self.prompt_session and self.prompt_session.app:
            self.placeholder = self.prompt_session.app.current_buffer.text
            self.interrupted = True
            self.prompt_session.app.exit()
