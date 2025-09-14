import functools
from typing import TYPE_CHECKING, List, Optional

from rich.console import Console
from rich.markdown import Markdown

from byte.context import get_container

if TYPE_CHECKING:
    pass


def pause_live_display(func):
    """Decorator to pause any active Live display during interactive input."""

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        container = get_container()

        # Check if there's an active response handler with live display
        try:
            response_handler = await container.make("response_handler")
            # Store reference to any active live display
            active_live = getattr(response_handler, "_active_live", None)

            if active_live and active_live.is_started:
                # Print current content and stop live display
                if (
                    hasattr(response_handler, "_accumulated_content")
                    and response_handler._accumulated_content
                ):
                    active_live.console.print(
                        Markdown(response_handler._accumulated_content)
                    )
                active_live.stop()
                live_was_active = True
            else:
                live_was_active = False

        except Exception:
            live_was_active = False
            active_live = None

        try:
            # Execute the interactive function
            return await func(self, *args, **kwargs)
        finally:
            # Restart live display if it was active
            if live_was_active and active_live:
                active_live.start()

    return wrapper


class InteractionService:
    """Service for user interactions during agent execution.

    Provides standardized methods for getting user input during tool execution
    or command processing, with consistent styling and error handling.
    Usage: `await interaction_service.confirm("Delete this file?")` -> bool response
    """

    @pause_live_display
    async def confirm(self, message: str, default: bool = False) -> bool:
        """Ask user for yes/no confirmation with default value.

        Usage: `confirmed = await interaction_service.confirm("Proceed?", default=True)`
        """
        suffix = " (Y/n)" if default else " (y/N)"

        try:
            container = get_container()
            console: Console = await container.make("console")

            while True:
                console.print(f"\n{message}{suffix}: ", end="")
                result = (console.input()).strip().lower()

                if not result:
                    return default

                if result in ["y", "yes"]:
                    return True
                elif result in ["n", "no"]:
                    return False
                else:
                    console.print("Please enter 'y' or 'n'")
                    continue

        except (EOFError, KeyboardInterrupt):
            # Fallback if container/console not available
            return default

    @pause_live_display
    async def select(
        self, message: str, choices: List[str], default: Optional[str] = None
    ) -> str:
        """Ask user to select from multiple options.

        Usage: `choice = await interaction_service.select("Pick one:", ["a", "b", "c"])`
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")

        try:
            container = get_container()
            console: Console = await container.make("console")

            # Display options
            console.print(f"\n{message}")
            for i, choice in enumerate(choices, 1):
                marker = " (default)" if choice == default else ""
                console.print(f"  {i}. {choice}{marker}")

            while True:
                try:
                    console.print("Enter choice number: ", end="")
                    response = (console.input()).strip()

                    # Handle empty response with default
                    if not response and default:
                        return default

                    # Parse numeric choice
                    choice_num = int(response)
                    if 1 <= choice_num <= len(choices):
                        return choices[choice_num - 1]
                    else:
                        console.print(
                            f"Please enter a number between 1 and {len(choices)}"
                        )

                except (ValueError, EOFError, KeyboardInterrupt):
                    if default:
                        return default
                    console.print("Invalid input. Please enter a number.")

        except Exception:
            # Fallback if container/console not available
            if default:
                return default
            return choices[0] if choices else ""

    @pause_live_display
    async def input_text(self, message: str, default: str = "") -> str:
        """Ask user for text input with optional default.

        Usage: `text = await interaction_service.input_text("Enter name:", "default_name")`
        """
        try:
            container = get_container()
            console: Console = await container.make("console")

            suffix = f" [{default}]" if default else ""
            console.print(f"{message}{suffix}: ", end="")
            response = (console.input()).strip()
            return response or default
        except (EOFError, KeyboardInterrupt):
            return default
        except Exception:
            # Fallback if container/console not available
            return default
