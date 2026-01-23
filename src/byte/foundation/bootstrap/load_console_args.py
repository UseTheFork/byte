from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from byte.config import Repository
from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


# TODO: Doc String
class LoadConsoleArgs(Bootstrapper):
    """"""

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap environment variable loading.

        Args:
            app: The application instance.
        """
        args = app.instance("args", Repository())
        self.parse_args(app, args)

    def parse_args(self, app: Application, config: Repository):
        """Parse command-line arguments into the repository.

        Stores:
        - raw: Full argv list
        - script: Script name (argv[0])
        - command: First positional argument (if any)
        - flags: List of flags (--flag, -f)
        - options: Dict of options (--key=value, --key value)
        - positional: List of positional arguments
        """
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
