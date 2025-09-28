from langchain_core.tools import tool

from byte.context import make
from byte.domain.cli_input.service.interactions_service import InteractionService


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
