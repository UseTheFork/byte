from typing import Type

from byte.domain.agent.base import BaseAgent
from byte.domain.events.event import Event


class ExitRequested(Event):
    """Event emitted when the application should exit gracefully.

    Usage: `await self.event(ExitRequested())` -> triggers application shutdown
    """

    pass


class PrePrompt(Event):
    """Event emitted before each user prompt to allow commands to display contextual information.

    Usage: `await self.event(PrePrompt(current_agent="coder"))` -> triggers pre-prompt displays
    """

    current_agent: Type[BaseAgent]


class PromptRefresh(Event):
    """Event fired when the prompt loop should refresh immediately.

    Triggers the main loop to break out of waiting for user input
    and restart the prompt cycle, useful for file watcher notifications.
    Usage: `await self.event(PromptRefresh(reason="Added file due to AI comment"))`
    """

    reason: str = ""
