from typing import TYPE_CHECKING, List, Optional

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import confirm

if TYPE_CHECKING:
    from byte.container import Container


class InteractionService:
    """Service for user interactions during agent execution.

    Provides standardized methods for getting user input during tool execution
    or command processing, with consistent styling and error handling.
    Usage: `await interaction_service.confirm("Delete this file?")` -> bool response
    """

    def __init__(self, container: Optional["Container"] = None):
        self.container = container

    async def confirm(self, message: str, default: bool = False) -> bool:
        """Ask user for yes/no confirmation with default value.

        Usage: `confirmed = await interaction_service.confirm("Proceed?", default=True)`
        """
        try:
            # Use prompt_toolkit's confirm for consistent UX
            suffix = " (Y/n)" if default else " (y/N)"
            return confirm(f"{message}{suffix}")
        except (EOFError, KeyboardInterrupt):
            # User cancelled - return the opposite of default to be safe
            return not default

    async def select(
        self, message: str, choices: List[str], default: Optional[str] = None
    ) -> str:
        """Ask user to select from multiple options.

        Usage: `choice = await interaction_service.select("Pick one:", ["a", "b", "c"])`
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")

        # Display options
        print(f"\n{message}")
        for i, choice in enumerate(choices, 1):
            marker = " (default)" if choice == default else ""
            print(f"  {i}. {choice}{marker}")

        while True:
            try:
                response = prompt("Enter choice number: ").strip()

                # Handle empty response with default
                if not response and default:
                    return default

                # Parse numeric choice
                choice_num = int(response)
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}")

            except (ValueError, EOFError, KeyboardInterrupt):
                if default:
                    return default
                print("Invalid input. Please enter a number.")

    async def input_text(self, message: str, default: str = "") -> str:
        """Ask user for text input with optional default.

        Usage: `text = await interaction_service.input_text("Enter name:", "default_name")`
        """
        try:
            suffix = f" [{default}]" if default else ""
            response = prompt(f"{message}{suffix}: ")
            return response.strip() or default
        except (EOFError, KeyboardInterrupt):
            return default

    async def input_multiline(self, message: str) -> str:
        """Ask user for multi-line text input.

        Usage: `text = await interaction_service.input_multiline("Enter description:")`
        """
        print(f"{message} (Press Ctrl+D or Ctrl+Z to finish):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            pass
        return "\n".join(lines)
