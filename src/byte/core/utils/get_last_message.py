def get_last_message(state):
    """Extract the last message from a state dict or list.

    Handles both list-based states and dict-based states with a "history_messages" key.
    Raises ValueError if no messages are found.

    Usage: `last_msg = get_last_message(state)` -> most recent message
    """
    if isinstance(state, list):
        if not state:
            raise ValueError("No messages found in empty list state")
        return state[-1]
    elif messages := state.get("history_messages", []):
        return messages[-1]
    else:
        raise ValueError(f"No messages found in input state: {state}")
