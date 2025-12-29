def extract_json_from_message(message) -> str:
    """ """
    if isinstance(message.content, list) and message.content:
        return message.content[0].get("partial_json", "")

    return ""
