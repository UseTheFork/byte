from typing import List, Optional

from rich.prompt import Prompt

from byte.core.service.base_service import Service
from byte.domain.cli.service.console_service import ConsoleService


class InteractionService(Service):
    """Service for user interactions during agent execution.

    Provides standardized methods for getting user input during tool execution
    or command processing, with consistent styling and error handling.
    Usage: `await interaction_service.confirm("Delete this file?")` -> bool response
    """

    async def confirm(self, message: str, default: bool = False) -> bool | None:
        """Ask user for yes/no confirmation with default value.

        Usage: `confirmed = await interaction_service.confirm("Proceed?", default=True)`
        """

        try:
            console = await self.make(ConsoleService)

            return console.confirm(
                message=f"{message}",
                default=default,
            )

        except EOFError:
            # Fallback if container/console not available
            return default

    async def select(self, message: str, choices: List[str], default: Optional[str] = None) -> str | None:
        """Ask user to select from multiple options.

        Usage: `choice = await interaction_service.select("Pick one:", ["a", "b", "c"])`
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")

        try:
            console = await self.make(ConsoleService)

            # Determine starting index if default provided
            start_index = 0
            if default and default in choices:
                start_index = choices.index(default)

            result = console.select(*choices, title=message, start_index=start_index)

            # If user pressed escape, return default or first choice
            if result is None:
                if default:
                    return default
                return choices[0] if choices else ""

            return result

        except EOFError:
            if default:
                return default
            return choices[0] if choices else ""
        except Exception:
            # Fallback if container/console not available
            if default:
                return default
            return choices[0] if choices else ""

    async def select_numbered(self, message: str, choices: List[str], default: Optional[int] = None) -> str | None:
        """Ask user to select from numbered options.

        Displays choices as a numbered list and prompts for selection by number.
        Usage: `choice = await interaction_service.select_numbered("Pick one:", ["a", "b", "c"], default=1)`
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")

        try:
            console = await self.make(ConsoleService)

            # Determine starting index if default provided (convert 1-based to 0-based)
            start_index = 0
            if default and 1 <= default <= len(choices):
                start_index = default - 1

            result = console.select(*choices, title=message, start_index=start_index)

            # If user pressed escape, return default or first choice
            if result is None:
                if default and 1 <= default <= len(choices):
                    return choices[default - 1]
                return choices[0] if choices else ""

            return result

        except (EOFError, KeyboardInterrupt):
            if default and 1 <= default <= len(choices):
                return choices[default - 1]
            return choices[0] if choices else ""
        except Exception:
            # Fallback if container/console not available
            if default and 1 <= default <= len(choices):
                return choices[default - 1]
            return choices[0] if choices else ""

    async def input_text(self, message: str, default: str = "") -> str:
        """Ask user for text input with optional default.

        Usage: `text = await interaction_service.input_text("Enter name:", "default_name")`
        """
        try:
            console = await self.make(ConsoleService)

            result = Prompt.ask(
                message,
                console=console.console,
                default=default if default else None,
            )
            return str(result)

        except (EOFError, KeyboardInterrupt):
            return default
        except Exception:
            # Fallback if container/console not available
            return default

    async def confirm_or_input(
        self, confirm_message: str, input_message: str, default_confirm: bool = True
    ) -> tuple[bool, Optional[str]]:
        """Ask user for confirmation, then prompt for text input if they decline.

        Returns a tuple of (confirmed: bool, text_input: Optional[str]).
        If user confirms, returns (True, None).
        If user declines, prompts for text and returns (False, user_input).
        Usage: `confirmed, text = await interaction_service.confirm_or_input("Use default?", "Enter custom value:")`
        """
        try:
            # First ask for confirmation
            confirmed = await self.confirm(confirm_message, default=default_confirm)

            if confirmed:
                return (True, None)

            # If not confirmed, prompt for text input
            console = await self.make(ConsoleService)
            text_input = Prompt.ask(
                input_message,
                console=console.console,
            )
            return (False, text_input)

        except (EOFError, KeyboardInterrupt):
            # Return default confirmation on interrupt
            return (default_confirm, None)
        except Exception:
            # Fallback if container/console not available
            return (default_confirm, None)
