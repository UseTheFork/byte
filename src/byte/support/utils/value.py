from collections.abc import Callable


def value(val, *args, **kwargs):
    """Return the default value of the given value.

    If the value is callable, invoke it with the provided arguments.
    Otherwise, return the value as-is.
    Usage: `result = value(lambda: expensive_operation())` or `result = value(42)`
    """

    return val(*args, **kwargs) if isinstance(val, Callable) else val
