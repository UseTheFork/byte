import inspect
import logging
from typing import TYPE_CHECKING

from loguru import logger

from byte import Service

if TYPE_CHECKING:
    pass


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


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

        third_party_log_file = self.app.cache_path("third_party.log")
        third_party_log_file.write_text("")

        config = {
            "handlers": [
                {
                    "sink": log_file,
                    "level": "DEBUG",
                    "serialize": False,
                    "backtrace": True,
                    "filter": lambda record: record["name"].startswith("byte"),
                },
                {
                    "sink": third_party_log_file,
                    "level": "DEBUG",
                    "serialize": False,
                    "filter": lambda record: not record["name"].startswith("byte"),
                },
            ],
        }

        # TODO: Check env before setting up above sinks.
        logger.configure(**config)

        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        self.log = logger

    # TODO: need to figure this out.
    def _should_log_to_console(self, record) -> bool:
        """Filter function to only log to Rich when console is not in live mode."""
        try:
            return not self.app["console"].is_live()
        except KeyError, AttributeError:
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
