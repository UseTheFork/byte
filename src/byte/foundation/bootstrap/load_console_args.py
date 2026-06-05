import sys
from typing import TYPE_CHECKING

from byte.config import Repository
from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class LoadConsoleArgs(Bootstrapper):
    """Load and parse command-line arguments."""

    def bootstrap(self, app: Application) -> None:
        """Parse command-line arguments into the repository."""
        args = app.instance("args", Repository())
        self.parse_args(app, args)

    def parse_args(self, app: Application, config: Repository) -> None:
        """Parse command-line arguments into the repository."""
        argv = sys.argv[1:]  # Skip script name

        config.add("raw", sys.argv)
        config.add("script", sys.argv[0])

        flags = []
        options = {}
        positional = []

        i = 0
        while i < len(argv):
            arg = argv[i]

            if arg.startswith("--"):
                # Long option: --key=value or --key value or --flag
                if "=" in arg:
                    key, value = arg[2:].split("=", 1)
                    # Handle multiple values for same key
                    if key in options:
                        if not isinstance(options[key], list):
                            options[key] = [options[key]]
                        options[key].append(value)
                    else:
                        options[key] = value
                elif i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                    key = arg[2:]
                    value = argv[i + 1]
                    # Handle multiple values for same key
                    if key in options:
                        if not isinstance(options[key], list):
                            options[key] = [options[key]]
                        options[key].append(value)
                    else:
                        options[key] = value
                    i += 1
                else:
                    flags.append(arg[2:])
            elif arg.startswith("-"):
                # Short flag: -f
                flags.append(arg[1:])
            else:
                # Positional argument
                positional.append(arg)

            i += 1

        config.add("command", positional[0] if positional else None)
        config.add("flags", flags)
        config.add("options", options)
        config.add("positional", positional)
