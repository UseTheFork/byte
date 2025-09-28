from typing import TYPE_CHECKING, Optional, TypeVar

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
        from byte.domain.cli_input.service.interactions_service import (
            InteractionService,
        )

        if not self.container:
            raise RuntimeError(
                "No container available - ensure service is properly initialized"
            )

        interaction_service = await self.container.make(InteractionService)
        return await interaction_service.input_text(message)

    async def prompt_for_confirmation(self, message: str, default: bool = True):
        """Prompt the user for yes/no confirmation with a custom message.

        Displays a confirmation dialog and waits for user response with
        automatic timeout handling. Returns the default value on timeout.
        Usage: `confirmed = await self.prompt_for_confirmation("Delete file?", False)`
        """
        from byte.domain.cli_input.service.interactions_service import (
            InteractionService,
        )

        if not self.container:
            raise RuntimeError(
                "No container available - ensure service is properly initialized"
            )

        interaction_service = await self.container.make(InteractionService)
        return await interaction_service.confirm(message, default)
