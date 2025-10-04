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

            result = Prompt.ask(
                message,
                console=console,
                choices=choices,
                default=default if default and default in choices else None,
                case_sensitive=False,
            )

            return result

        except (EOFError, KeyboardInterrupt):
            if default:
                return default
            return choices[0] if choices else ""
        except Exception:
            # Fallback if container/console not available
            if default:
                return default
            return choices[0] if choices else ""

    async def select_numbered(
        self, message: str, choices: List[str], default: Optional[int] = None
    ) -> str:
        """Ask user to select from numbered options.

        Displays choices as a numbered list and prompts for selection by number.
        Usage: `choice = await interaction_service.select_numbered("Pick one:", ["a", "b", "c"], default=1)`
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")

        try:
            console: Console = await self.make(Console)

            # Display numbered options
            console.print(f"\n{message}")
            for idx, choice in enumerate(choices, 1):
                console.print(f"  {idx}. {choice}")

            # Create valid number choices as strings
            valid_choices = [str(i) for i in range(1, len(choices) + 1)]
            default_str = (
                str(default) if default and 1 <= default <= len(choices) else None
            )

            # Prompt for number selection
            selection = Prompt.ask(
                "Enter number",
                console=console,
                choices=valid_choices,
                default=default_str,
            )

            # Return the actual choice string
            return choices[int(selection) - 1]

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
