import sys

from rich.pretty import pprint


def dump(*args, **kwargs):
    """Debug function that pretty prints variables using rich.

    Usage:
    dump(variable1, variable2)
    dump(locals())
    dump(globals())
    """
    if not args and not kwargs:
        # If no arguments, dump the caller's locals
        import inspect

        frame = inspect.currentframe().f_back
        pprint(frame.f_locals)
    else:
        # Print each argument
        for arg in args:
            pprint(arg)

        # Print keyword arguments
        if kwargs:
            pprint(kwargs)


def dd(*args, **kwargs):
    """Debug function that dumps variables and then exits.

    Usage:
    dd(variable1, variable2)  # Prints variables and exits
    dd(locals())  # Prints local scope and exits
    """
    dump(*args, **kwargs)
    sys.exit(1)


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
