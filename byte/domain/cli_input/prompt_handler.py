from typing import AsyncGenerator

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory

from byte.context import make
from byte.core.config.config import BYTE_DIR
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


class PromptHandler:
    def __init__(self):
        self.completer = CommandCompleter()
        self.session = PromptSession(
            history=FileHistory(BYTE_DIR / ".input_history"),
            multiline=False,
            completer=self.completer,
        )

    async def initialize(self):
        """Initialize async components."""
        # The completer will initialize itself lazily in get_completions_async
        pass

    async def get_input_async(self, message: str = "> ") -> str:
        """Get user input using prompt_toolkit async."""
        try:
            return await self.session.prompt_async(message)
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt  # Re-raise instead of returning empty string
