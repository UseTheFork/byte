from typing import TYPE_CHECKING, List, Optional

from langchain_core.tools import tool

from byte.context import get_container

if TYPE_CHECKING:
    from byte.domain.ui.interactions import InteractionService


@tool
async def user_confirm(message: str, default: bool = False) -> bool:
    """Ask the user for yes/no confirmation before proceeding with an action.

    Args:
        message: The confirmation message to display to the user
        default: Default response if user just presses enter
    """
    container = get_container()

    interaction_service: InteractionService = await container.make(
        "interaction_service"
    )
    return await interaction_service.confirm(message, default)


@tool
async def user_input(message: str, default: str = "") -> str:
    """Get text input from the user during agent execution.

    Args:
        message: The prompt message to display to the user
        default: Default value if user provides no input
    """
    container = get_container()

    interaction_service: InteractionService = await container.make(
        "interaction_service"
    )
    return await interaction_service.input_text(message, default)


@tool
async def user_select(
    message: str, choices: List[str], default: Optional[str] = None
) -> str:
    """Present multiple choices to the user and get their selection.

    Args:
        message: The prompt message to display to the user
        choices: List of choices to present to the user
        default: Default choice if user provides no input
    """
    container = get_container()

    interaction_service: InteractionService = await container.make(
        "interaction_service"
    )
    return await interaction_service.select(message, choices, default)
