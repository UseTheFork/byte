from typing import AsyncGenerator

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory

from byte.context import make
from byte.core.command.registry import CommandRegistry


class CommandCompleter(Completer):
    def __init__(self):
        self.command_registry = None

    def get_completions(self, document: Document, complete_event):
        pass

    async def get_completions_async(
        self, document: Document, complete_event
    ) -> AsyncGenerator[Completion, None]:
        """Async generator for completions using prompt_toolkit 3.0's native async support."""
        if not self.command_registry:
            self.command_registry = await make(CommandRegistry)

        text = document.text_before_cursor

        if text.startswith("/"):
            # Parse slash command
            if " " in text:
                cmd_part, args_part = text.split(" ", 1)
                cmd_name = cmd_part[1:]  # Remove /
                command = self.command_registry.get_slash_command(cmd_name)
                if command:
                    completions = await command.get_completions(args_part)
                    # Only replace the args part, not the whole command
                    for completion in completions:
                        yield Completion(completion, start_position=-len(args_part))
                return
            else:
                # Complete command names
                cmd_prefix = text[1:]  # Remove /
                for cmd_name in self.command_registry._slash_commands.keys():
                    if cmd_name.startswith(cmd_prefix):
                        yield Completion(cmd_name, start_position=-len(cmd_prefix))
                return


class PromptHandler:
    def __init__(self):
        self.completer = CommandCompleter()
        self.session = PromptSession(
            history=InMemoryHistory(),
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
