from typing import List

from langchain_core.messages import AIMessage


def get_last_ai_message(messages: List) -> AIMessage:
    """Extract the last AIMessage from a list of messages.

    Iterates through the messages list in reverse to find the most recent AIMessage.
    Raises ValueError if no AIMessage is found.

    Usage: `last_ai_msg = get_last_ai_message(messages)` -> most recent AIMessage
    """
    if not messages:
        raise ValueError("No messages found in empty list")

    for message in reversed(messages):
        if isinstance(message, AIMessage):
            return message

    raise ValueError("No AIMessage found in messages list")
