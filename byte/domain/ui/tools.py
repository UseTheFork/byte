from typing import TYPE_CHECKING, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from byte.container import Container
    from byte.domain.ui.interactions import InteractionService


class ConfirmInput(BaseModel):
    """Input schema for confirm tool."""

    message: str = Field(description="The confirmation message to show the user")
    default: bool = Field(
        default=False, description="Default value if user doesn't respond"
    )


class ConfirmTool(BaseTool):
    """Tool for agents to ask user for yes/no confirmation.

    Enables agents to pause execution and get user approval before
    proceeding with potentially destructive or important actions.
    Usage: Agent calls `confirm("Delete this file?")` -> waits for user response
    """

    name: str = "confirm"
    description: str = "Ask the user for yes/no confirmation before proceeding"
    args_schema = ConfirmInput

    def __init__(self, container: Optional["Container"] = None):
        super().__init__()
        self.container = container

    async def _arun(self, message: str, default: bool = False) -> bool:
        """Execute confirmation request asynchronously."""
        if not self.container:
            # Fallback if no container available
            return default

        try:
            interaction_service: InteractionService = await self.container.make(
                "interaction_service"
            )
            return await interaction_service.confirm(message, default)
        except Exception:
            # Safe fallback on any error
            return default

    def _run(self, message: str, default: bool = False) -> bool:
        """Synchronous execution (not recommended for interactive tools)."""
        import asyncio

        return asyncio.run(self._arun(message, default))


class UserInputInput(BaseModel):
    """Input schema for user input tool."""

    message: str = Field(description="The prompt message to show the user")
    default: str = Field(
        default="", description="Default value if user doesn't respond"
    )


class UserInputTool(BaseTool):
    """Tool for agents to get text input from the user.

    Allows agents to request specific information from the user during
    execution, enabling interactive workflows and dynamic responses.
    Usage: Agent calls `user_input("What should I name this function?")` -> gets user response
    """

    name: str = "user_input"
    description: str = "Get text input from the user"
    args_schema = UserInputInput

    def __init__(self, container: Optional["Container"] = None):
        super().__init__()
        self.container = container

    async def _arun(self, message: str, default: str = "") -> str:
        """Execute input request asynchronously."""
        if not self.container:
            return default

        try:
            interaction_service: InteractionService = await self.container.make(
                "interaction_service"
            )
            return await interaction_service.input_text(message, default)
        except Exception:
            return default

    def _run(self, message: str, default: str = "") -> str:
        """Synchronous execution (not recommended for interactive tools)."""
        import asyncio

        return asyncio.run(self._arun(message, default))


class SelectInput(BaseModel):
    """Input schema for select tool."""

    message: str = Field(description="The selection prompt to show the user")
    choices: list[str] = Field(
        description="List of choices for the user to select from"
    )
    default: Optional[str] = Field(
        default=None, description="Default choice if user doesn't respond"
    )


class SelectTool(BaseTool):
    """Tool for agents to present multiple choice selections to the user.

    Enables agents to offer structured choices and get user preferences
    for decision-making during task execution.
    Usage: Agent calls `select("Choose approach:", ["option1", "option2"])` -> gets user choice
    """

    name: str = "select"
    description: str = "Present multiple choices to the user and get their selection"
    args_schema = SelectInput

    def __init__(self, container: Optional["Container"] = None):
        super().__init__()
        self.container = container

    async def _arun(
        self, message: str, choices: list[str], default: Optional[str] = None
    ) -> str:
        """Execute selection request asynchronously."""
        if not self.container or not choices:
            return default or (choices[0] if choices else "")

        try:
            interaction_service: InteractionService = await self.container.make(
                "interaction_service"
            )
            return await interaction_service.select(message, choices, default)
        except Exception:
            return default or (choices[0] if choices else "")

    def _run(
        self, message: str, choices: list[str], default: Optional[str] = None
    ) -> str:
        """Synchronous execution (not recommended for interactive tools)."""
        import asyncio

        return asyncio.run(self._arun(message, choices, default))
