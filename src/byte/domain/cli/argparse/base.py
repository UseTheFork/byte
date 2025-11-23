from argparse import ArgumentParser


class ByteArgumentParser(ArgumentParser):
    """Custom ArgumentParser for Byte commands with sensible defaults.

    Disables automatic exit on error and help flag to allow custom error
    handling and help text generation within the command system.
    Usage: `parser = ByteArgumentParser(prog="command_name", description="...")`
    """

    def __init__(self, *args, **kwargs):
        """Initialize parser with exit_on_error=False and add_help=False by default."""
        kwargs.setdefault("exit_on_error", False)
        kwargs.setdefault("add_help", False)
        # kwargs.setdefault("usage", "/%(prog)s [options]")
        super().__init__(*args, **kwargs)
