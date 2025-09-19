from typing import List, Optional

from langchain_core.tools import tool

from byte.context import make
from byte.domain.ui.interactions import InteractionService


@tool(parse_docstring=True)
async def user_confirm(
    message: str,
    default: bool = False,
) -> bool:
    """Ask the user for yes/no confirmation before proceeding with an action.

    Args:
        message: The confirmation message to display to the user
        default: Default response if user just presses enter
    """

    interaction_service = await make(InteractionService)
    return await interaction_service.confirm(message, default)


@tool(parse_docstring=True)
async def user_input(message: str, default: str = "") -> str:
    """Get text input from the user during agent execution.

    Args:
        message: The prompt message to display to the user
        default: Default value if user provides no input
    """

    interaction_service = await make(InteractionService)
    return await interaction_service.input_text(message, default)


@tool(parse_docstring=True)
async def user_select(
    message: str,
    choices: List[str],
    default: Optional[str] = None,
) -> str:
    """Present multiple choices to the user and get their selection.

    Args:
        message: The prompt message to display to the user
        choices: List of choices to present to the user
        default: Default choice if user provides no input
    """

    interaction_service = await make(InteractionService)
    return await interaction_service.select(message, choices, default)
