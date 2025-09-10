"""Common helper functions for ByteSmith."""

from typing import Any, Dict


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    return data.get(key, default)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
