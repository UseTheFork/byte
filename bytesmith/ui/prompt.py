from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory

from bytesmith.commands.registry import command_registry


class CommandCompleter(Completer):
    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor

        if text.startswith("/"):
            completions = command_registry.get_slash_completions(text)
        elif text.startswith("@"):
            completions = command_registry.get_at_completions(text)
        else:
            completions = []

        for completion in completions:
            yield Completion(completion, start_position=-len(text))


class PromptHandler:
    def __init__(self):
        self.session = PromptSession(
            history=InMemoryHistory(),
            multiline=False,
            completer=CommandCompleter(),
        )

    async def get_input_async(self, message: str = "> ") -> str:
        """Get user input using prompt_toolkit async."""
        try:
            return await self.session.prompt_async(message)
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt  # Re-raise instead of returning empty string
