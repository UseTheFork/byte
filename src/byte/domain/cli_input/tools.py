import asyncio
from typing import List, Optional, cast

from langchain_core.tools import tool

from byte.context import make
from byte.core.actors.message import Message, MessageBus, MessageType
from byte.domain.cli_input.actor.user_interaction_actor import UserInteractionActor
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

    message_bus = await make(MessageBus)
    if not message_bus:
        raise RuntimeError(
            "No Message Bus available - ensure service is properly initialized"
        )

    response_queue = asyncio.Queue()

    await message_bus.send_to(
        UserInteractionActor,
        Message(
            type=MessageType.REQUEST_USER_CONFIRM,
            payload={
                "message": message,
                "default": default,
            },
            reply_to=response_queue,
        ),
    )

    try:
        response = await asyncio.wait_for(response_queue.get(), timeout=30.0)
        return cast(bool, response.payload["input"])
    except TimeoutError:
        return default


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
