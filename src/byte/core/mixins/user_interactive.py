from typing import TYPE_CHECKING, Optional, TypeVar

from byte.domain.cli.service.interactions_service import (
    InteractionService,
)

if TYPE_CHECKING:
    from byte.container import Container

T = TypeVar("T")


class UserInteractive:
    """Mixin that provides user interaction capabilities through the input actor.

    Enables services to prompt users for input or confirmation through the
    actor system. Handles message routing and response collection automatically.
    Usage: `class MyService(UserInteractive): result = await self.prompt_for_confirmation("Continue?", True)`
    """

    container: Optional["Container"]

    async def prompt_for_input(self, message):
        """Prompt the user for general input via the input actor.

        Sends a request to the UserInteractionActor to display the input prompt,
        returning control to the user for general text input.
        Usage: `await self.prompt_for_input()` -> shows input prompt to user
        """

        if not self.container:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = await self.container.make(InteractionService)
        return await interaction_service.input_text(message)

    async def prompt_for_confirmation(self, message: str, default: bool = True):
        """Prompt the user for yes/no confirmation with a custom message.

        Displays a confirmation dialog and waits for user response with
        automatic timeout handling. Returns the default value on timeout.
        Usage: `confirmed = await self.prompt_for_confirmation("Delete file?", False)`
        """

        if not self.container:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = await self.container.make(InteractionService)
        return await interaction_service.confirm(message, default)

    async def prompt_for_select(self, message: str, choices: list[str], default: str | None = None) -> str | None:
        """Prompt the user to select from multiple options.

        Displays a list of choices and waits for user selection with
        optional default value for timeout or errors.
        Usage: `choice = await self.prompt_for_select("Pick one:", ["option1", "option2"], "option1")`
        """

        if not self.container:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = await self.container.make(InteractionService)
        return await interaction_service.select(message, choices, default)

    async def prompt_for_select_numbered(
        self, message: str, choices: list[str], default: int | None = None
    ) -> str | None:
        """Prompt the user to select from numbered options.

        Displays choices as a numbered list and prompts for selection by number.
        Usage: `choice = await self.prompt_for_select_numbered("Pick one:", ["option1", "option2"], default=1)`
        """

        if not self.container:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = await self.container.make(InteractionService)
        return await interaction_service.select_numbered(message, choices, default)

    async def prompt_for_confirm_or_input(
        self, confirm_message: str, input_message: str, default_confirm: bool = True
    ) -> tuple[bool, Optional[str]]:
        """Prompt user for confirmation, then text input if they decline.

        First asks for yes/no confirmation. If user declines, prompts for text input.
        Returns tuple of (confirmed: bool, text: Optional[str]).
        Usage: `confirmed, text = await self.prompt_for_confirm_or_input("Use default?", "Enter value:")`
        """

        if not self.container:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = await self.container.make(InteractionService)
        return await interaction_service.confirm_or_input(confirm_message, input_message, default_confirm)
