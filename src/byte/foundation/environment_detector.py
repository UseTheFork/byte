from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from byte.foundation import Application

from typing import Callable


class EnvironmentDetector:
    """Detect the application's current environment."""

    def detect(self, callback: Callable, app: Application) -> str:
        """
        Detect the application's current environment.

        Args:
            callback: Closure that returns the environment name.
            console_args: Console arguments to check for --env flag.

        Returns:
            Environment name.
        """
        value = app["args"].get("options", {}).get("env", None)
        if value is not None:
            return value

        env_var = os.getenv("BYTE_ENV")
        if env_var is not None:
            return env_var

        return callback()
