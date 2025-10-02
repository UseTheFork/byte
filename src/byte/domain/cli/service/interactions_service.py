from typing import List, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt

from byte.core.service.base_service import Service


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

        try:
            console = await self.make(Console)

            return Confirm.ask(
                prompt=f"{message}",
                default=default,
                console=console,
                case_sensitive=False,
            )

        except EOFError:
            # Fallback if container/console not available
            return default

    async def select(
        self, message: str, choices: List[str], default: Optional[str] = None
    ) -> str:
        """Ask user to select from multiple options.

        Usage: `choice = await interaction_service.select("Pick one:", ["a", "b", "c"])`
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")

        try:
            console: Console = await self.make(Console)

            # Display options
            console.print(f"\n{message}")
            for i, choice in enumerate(choices, 1):
                marker = " (default)" if choice == default else ""
                console.print(f"  {i}. {choice}{marker}")

            # Create choices for Prompt.ask (1, 2, 3, etc.)
            choice_numbers = [str(i) for i in range(1, len(choices) + 1)]

            result = Prompt.ask(
                "Enter choice number",
                console=console,
                choices=choice_numbers,
                default=str(choices.index(default) + 1)
                if default and default in choices
                else None,
            )

            # Convert back to actual choice
            choice_index = int(result) - 1
            return choices[choice_index]

        except (EOFError, KeyboardInterrupt):
            if default:
                return default
            return choices[0] if choices else ""
        except Exception:
            # Fallback if container/console not available
            if default:
                return default
            return choices[0] if choices else ""

    async def input_text(self, message: str, default: str = "") -> str:
        """Ask user for text input with optional default.

        Usage: `text = await interaction_service.input_text("Enter name:", "default_name")`
        """
        try:
            console: Console = await self.make(Console)

            result = Prompt.ask(
                message,
                console=console,
                default=default if default else None,
            )
            return result

        except (EOFError, KeyboardInterrupt):
            return default
        except Exception:
            # Fallback if container/console not available
            return default
