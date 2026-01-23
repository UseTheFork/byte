from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from byte import Service

if TYPE_CHECKING:
    pass


class LogService(Service):
    """Logging service wrapper for Loguru with Rich integration.

    Configures logging with file output and Rich console handler,
    automatically clearing log files on boot and filtering console
    output based on live mode state.

    Usage: `log.info("message")` -> logs to file and console
    Usage: `log.debug("debug info")` -> logs debug information
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make sure we have a config and cache path
        self.app.config_path().mkdir(exist_ok=True)
        self.app.cache_path().mkdir(exist_ok=True)

        # Clear log files on boot
        log_file = self.app.cache_path("byte.log")
        log_file.write_text("")

        config = {
            "handlers": [
                {"sink": log_file, "level": "DEBUG", "serialize": False, "backtrace": True},
                # {
                #     "sink": RichHandler(markup=True),
                #     "level": "DEBUG",
                #     "format": "{message}",
                #     "filter": self._should_log_to_console,
                # },
            ],
        }

        # TODO: Check env before setting up above sinks.
        logger.configure(**config)

        self.log = logger

    # TODO: need to figure this out.
    def _should_log_to_console(self, record) -> bool:
        """Filter function to only log to Rich when console is not in live mode."""
        try:
            return not self.app["console"].is_live()
        except (KeyError, AttributeError):
            # Console not available yet, allow logging
            return True

    def __getattr__(self, name: str):
        """Proxy unknown method calls to the underlying Loguru logger.

        Allows direct access to Loguru logger methods not explicitly wrapped
        by this service, enabling full Loguru API access.

        Usage: `log.debug("message")` -> calls `log.log.debug("message")`
        Usage: `log.info("message")` -> calls `log.log.info("message")`
        """
        return getattr(self.log, name)
