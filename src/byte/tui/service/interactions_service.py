import asyncio
from typing import List, Optional, cast

from byte.support import Service
from byte.tui import InputCancelledError, Messages
from byte.tui.schemas import Answer, AnswerCancelled


class InteractionService(Service):
    """Service for user interactions during agent execution.

    Provides standardized methods for getting user input during tool execution
    or command processing, with consistent styling and error handling.
    Usage: `await interaction_service.confirm("Delete this file?")` -> bool response
    """

    async def confirm(self, message: str, default: bool = False) -> bool:
        """Ask user for yes/no confirmation with default value.

        Usage: `confirmed = await interaction_service.confirm("Proceed?", default=True)`
        """

        # Convert string choices to Answer objects
        answer_options = [
            Answer(label="Yes", value=True, is_default=default),
            Answer(label="No", value=False, is_default=not default),
        ]

        result_future: asyncio.Future[Answer | list[Answer] | str | AnswerCancelled] = asyncio.Future()
        await self.emit_tui(
            Messages.PromptUser(
                question=message,
                options=answer_options,
                prompt_type="select",
                result_future=result_future,
            )
        )

        await result_future
        answer = result_future.result()

        if isinstance(answer, AnswerCancelled):
            raise InputCancelledError

        return cast(Answer, answer).value

    async def select(self, message: str, choices: List[Answer]) -> Answer:
        """Ask user to select from multiple options.

        Usage: `choice = await interaction_service.select("Pick one:", ["a", "b", "c"])`
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")

        result_future: asyncio.Future[Answer | list[Answer] | str | AnswerCancelled] = asyncio.Future()
        await self.emit_tui(
            Messages.PromptUser(
                question=message,
                options=choices,
                prompt_type="select",
                result_future=result_future,
            )
        )

        await result_future
        answer = result_future.result()

        if isinstance(answer, AnswerCancelled):
            raise InputCancelledError

        return cast(Answer, answer)

    async def input_text(self, message: str) -> str:
        """Ask user for text input with optional default.

        Usage: `text = await interaction_service.input_text("Enter name:", "default_name")`
        """
        result_future: asyncio.Future[Answer | list[Answer] | str | AnswerCancelled] = asyncio.Future()
        await self.emit_tui(
            Messages.PromptUser(
                question=message,
                options=None,
                prompt_type="text",
                result_future=result_future,
            )
        )

        await result_future
        answer = result_future.result()

        if isinstance(answer, AnswerCancelled):
            raise InputCancelledError

        return cast(str, answer)

    async def confirm_or_input(
        self, confirm_message: str, input_message: str, default_confirm: bool = True
    ) -> tuple[bool, Optional[str]]:
        """Ask user for confirmation, then prompt for text input if they decline.

        Returns a tuple of (confirmed: bool, text_input: Optional[str]).
        If user confirms, returns (True, None).
        If user declines, prompts for text and returns (False, user_input).
        Usage: `confirmed, text = await interaction_service.confirm_or_input("Use default?", "Enter custom value:")`
        """
        # First ask for confirmation
        confirmed = await self.confirm(confirm_message, default=default_confirm)

        if confirmed:
            return (True, None)

        # If not confirmed, prompt for text input
        text_input = await self.input_text(input_message)
        return (False, text_input)
