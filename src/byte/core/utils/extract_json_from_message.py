def extract_json_from_message(message) -> str | None:
    """Extract partial JSON content from a message object.

    Usage: `json_str = extract_json_from_message(message)`
    """
    if isinstance(message.content, list) and message.content:
        return message.content[0].get("partial_json", None)

    return None
