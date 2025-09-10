from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory

from byte.core.command.registry import command_registry


class CommandCompleter(Completer):
    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor

        if text.startswith("/"):
            # Parse slash command
            if " " in text:
                cmd_part, args_part = text.split(" ", 1)
                cmd_name = cmd_part[1:]  # Remove /
                command = command_registry.get_slash_command(cmd_name)
                if command:
                    completions = command.get_completions(args_part)
                    # Only replace the args part, not the whole command
                    for completion in completions:
                        yield Completion(completion, start_position=-len(args_part))
                return
            else:
                # Complete command names
                cmd_prefix = text[1:]  # Remove /
                for cmd_name in command_registry._slash_commands.keys():
                    if cmd_name.startswith(cmd_prefix):
                        yield Completion(cmd_name, start_position=-len(cmd_prefix))
                return


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
