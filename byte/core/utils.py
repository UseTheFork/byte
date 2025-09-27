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
