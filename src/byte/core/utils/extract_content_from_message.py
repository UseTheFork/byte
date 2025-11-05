def extract_content_from_message(message) -> str:
    """Extract text content from message chunks with format-aware processing.

    Handles both string content and list-based content formats from different
    LLM providers, ensuring consistent text extraction across message types.
    Usage: `content = self._extract_content(chunk)` -> extracted text string
    """
    if isinstance(message.content, str):
        return message.content
    elif isinstance(message.content, list) and message.content:
        return message.content[0].get("text", "")

    raise ValueError(f"Unable to extract content from message: {type(message.content)}")
