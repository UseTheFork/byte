from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from rich.logging import RichHandler

if TYPE_CHECKING:
    from byte.foundation import Application


class Log:
    """Logging service wrapper for Loguru with Rich integration.

    Configures logging with file output and Rich console handler,
    automatically clearing log files on boot and filtering console
    output based on live mode state.

    Usage: `log.info("message")` -> logs to file and console
    Usage: `log.debug("debug info")` -> logs debug information
    """

    # TODO: need to figure this out.
    def _should_log_to_console(self, record) -> bool:
        """Filter function to only log to Rich when console is not in live mode."""
        try:
            return not self.app["console"].is_live()
        except (KeyError, AttributeError):
            # Console not available yet, allow logging
            return True

    def __init__(self, app: Application):
        self.app = app

        # Clear log files on boot
        log_file = self.app.cache_path("byte.log")
        log_file.write_text("")

        config = {
            "handlers": [
                {"sink": log_file, "level": "DEBUG", "serialize": False, "backtrace": True},
                {
                    "sink": RichHandler(markup=True),
                    "level": "INFO",
                    "format": "{message}",
                    "filter": self._should_log_to_console,
                },
            ],
        }

        # TODO: Check env before setting up above sinks.
        logger.configure(**config)

        self.log = logger

    def __getattr__(self, name: str):
        """Proxy unknown method calls to the underlying Loguru logger.

        Allows direct access to Loguru logger methods not explicitly wrapped
        by this service, enabling full Loguru API access.

        Usage: `log.debug("message")` -> calls `log.log.debug("message")`
        Usage: `log.info("message")` -> calls `log.log.info("message")`
        """
        return getattr(self.log, name)
