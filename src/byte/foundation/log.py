from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from byte.foundation import Application


class Log:
    """ """

    def __init__(self, app: Application):
        self.app = app

        # Clear log files on boot
        log_file = self.app.cache_path("byte.log")
        log_file.write_text("")

        config = {
            "handlers": [
                {"sink": log_file, "level": "DEBUG", "serialize": False, "backtrace": True},
                # {"sink": RichHandler(markup=True), "format": "{message}"},
            ],
        }

        # TODO: Check env before setting up above sinks.

        logger.configure(**config)

        self.log = logger

    def trace(self, *args, **kwargs) -> None:
        """Log a trace message.

        Usage: `log.trace("Trace information")`
        """
        self.log.trace(*args, **kwargs)

    def debug(self, *args, **kwargs) -> None:
        """Log a debug message.

        Usage: `log.debug("Debug information")`
        """
        self.log.debug(*args, **kwargs)

    def info(self, *args, **kwargs) -> None:
        """Log an info message.

        Usage: `log.info("Info message")`
        """
        self.log.info(*args, **kwargs)

    def success(self, *args, **kwargs) -> None:
        """Log a success message.

        Usage: `log.success("Operation successful")`
        """
        self.log.success(*args, **kwargs)

    def warning(self, *args, **kwargs) -> None:
        """Log a warning message.

        Usage: `log.warning("Warning message")`
        """
        self.log.warning(*args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        """Log an error message.

        Usage: `log.error("Error occurred")`
        """
        self.log.error(*args, **kwargs)

    def critical(self, *args, **kwargs) -> None:
        """Log a critical message.

        Usage: `log.critical("Critical issue")`
        """
        self.log.critical(*args, **kwargs)

    def exception(self, *args, **kwargs) -> None:
        """Log an exception with traceback.

        Usage: `log.exception("Exception occurred")`
        """
        self.log.exception(*args, **kwargs)
