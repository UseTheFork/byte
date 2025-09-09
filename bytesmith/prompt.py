from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory


class PromptHandler:
    def __init__(self):
        self.session = PromptSession(
            history=InMemoryHistory(),
            multiline=False,
        )

    async def get_input_async(self, message: str = "> ") -> str:
        """Get user input using prompt_toolkit async."""
        try:
            return await self.session.prompt_async(message)
        except (EOFError, KeyboardInterrupt):
            return ""
