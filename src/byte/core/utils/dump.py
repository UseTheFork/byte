import inspect
import sys

from rich.pretty import pprint


def dump(*args, **kwargs):
    """Debug function that pretty prints variables using rich.

    Usage:
    dump(variable1, variable2)
    dump(locals())
    dump(globals())
    """

    # Get caller information and build call stack
    frame = inspect.currentframe().f_back  # pyright: ignore[reportOptionalMemberAccess]
    filename = frame.f_code.co_filename  # pyright: ignore[reportOptionalMemberAccess]
    lineno = frame.f_lineno  # pyright: ignore[reportOptionalMemberAccess]

    # Trace the call stack
    call_chain = []
    current_frame = frame
    while current_frame is not None:
        frame_info = f"{current_frame.f_code.co_filename}:{current_frame.f_lineno} in {current_frame.f_code.co_name}()"
        call_chain.append(frame_info)
        current_frame = current_frame.f_back

    # Print location information
    pprint(f"Debug output from {filename}:{lineno}")
    pprint("Call chain:")
    for i, call in enumerate(call_chain):
        pprint(f"  {i}: {call}")

    if not args and not kwargs:
        # If no arguments, dump the caller's locals
        pprint(frame.f_locals)  # pyright: ignore[reportOptionalMemberAccess]
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
