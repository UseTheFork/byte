from typing import TYPE_CHECKING, Optional, TypeVar

from byte.tui import InteractionService
from byte.tui.schemas import Answer

if TYPE_CHECKING:
    from byte.foundation import Application

T = TypeVar("T")


class UserInteractive:
    """Provide user interaction capabilities through the input actor."""

    app: Application

    async def prompt_for_input(self, message) -> Answer:
        """Prompt the user for general text input."""

        if not self.app:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = self.app.make(InteractionService)
        return await interaction_service.input_text(message)

    async def prompt_for_confirmation(self, message: str, default: bool = True) -> bool:
        """Prompt the user for yes/no confirmation."""

        if not self.app:
            raise RuntimeError("No container available - ensure service is properly initialized")

        if self.app.running_unit_tests():
            return default

        interaction_service = self.app.make(InteractionService)
        return await interaction_service.confirm(message, default)

    async def prompt_for_select(self, message: str, choices: list[Answer]) -> Answer:
        """Prompt the user to select from multiple options."""

        if not self.app:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = self.app.make(InteractionService)
        return await interaction_service.select(message, choices)

    async def prompt_for_multiselect(self, message: str, choices: list[Answer]) -> list[Answer]:
        """Prompt the user to select multiple options from a list."""

        if not self.app:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = self.app.make(InteractionService)
        return await interaction_service.multi_select(message, choices)

    async def prompt_for_confirm_or_input(
        self, confirm_message: str, input_message: str, default_confirm: bool = True
    ) -> tuple[bool, Optional[Answer]]:
        """Prompt user for confirmation, then text input if they decline."""

        if not self.app:
            raise RuntimeError("No container available - ensure service is properly initialized")

        interaction_service = self.app.make(InteractionService)
        return await interaction_service.confirm_or_input(confirm_message, input_message, default_confirm)
