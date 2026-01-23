import inspect
import sys

from rich import inspect as rich_inspect
from rich.console import Console


def dump(*args, **kwargs):
    """Debug function that pretty prints variables using rich.

    Usage:
    dump(variable1, variable2)
    dump(locals())
    dump(globals())
    """
    console = Console()

    # Get caller information and build call stack
    frame = inspect.currentframe().f_back  # pyright: ignore[reportOptionalMemberAccess]  # ty:ignore[possibly-missing-attribute]
    filename = frame.f_code.co_filename  # pyright: ignore[reportOptionalMemberAccess]  # ty:ignore[possibly-missing-attribute]
    lineno = frame.f_lineno  # pyright: ignore[reportOptionalMemberAccess]  # ty:ignore[possibly-missing-attribute]

    # Trace the call stack
    call_chain = []
    current_frame = frame
    while current_frame is not None:
        frame_info = f"{current_frame.f_code.co_filename}:{current_frame.f_lineno} in {current_frame.f_code.co_name}()"
        call_chain.append(frame_info)
        current_frame = current_frame.f_back

    # Print location information
    console.print(f"Debug output from {filename}:{lineno}")
    console.print("Call chain:")
    for i, call in enumerate(call_chain):
        console.print(f"  {i}: {call}")

    if not args and not kwargs:
        # If no arguments, dump the caller's locals
        rich_inspect(frame.f_locals, all=False)  # pyright: ignore[reportOptionalMemberAccess]  # ty:ignore[possibly-missing-attribute]
    else:
        # Print each argument
        for arg in args:
            rich_inspect(arg, all=False)

        # Print keyword arguments
        if kwargs:
            rich_inspect(kwargs, all=False)


def dd(*args, **kwargs):
    """Debug function that dumps variables and then exits.

    Usage:
    dd(variable1, variable2)  # Prints variables and exits
    dd(locals())  # Prints local scope and exits
    """
    dump(*args, **kwargs)
    sys.exit(1)
