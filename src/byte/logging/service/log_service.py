import inspect
import logging
from collections.abc import Callable

from loguru import logger

from byte import Service


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
    """Configure logging with file output and Rich console handler."""

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
                    "filter": LogService._make_byte_log_filter(),
                },
                {
                    "sink": third_party_log_file,
                    "level": "DEBUG",
                    "serialize": False,
                    "filter": LogService._make_third_party_log_filter(),
                },
            ],
        }

        # TODO: Check env before setting up above sinks.
        logger.configure(**config)  # ty:ignore[invalid-argument-type]

        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        self.log = logger

    @staticmethod
    def _make_byte_log_filter() -> Callable[[dict], bool]:
        """Create a log filter that returns True when record name starts with any prefix."""

        def filter_func(record: dict) -> bool:
            return any(record["name"].startswith(prefix) for prefix in ["byte"])

        return filter_func

    @staticmethod
    def _make_third_party_log_filter() -> Callable[[dict], bool]:
        """Create a log filter that excludes third_party.log and filters by prefix."""

        prefixes = ["byte"]
        filtered_messages = ["third_party.log", "rust notify timeout"]

        def filter_func(record: dict) -> bool:
            if any(msg in record["message"] for msg in filtered_messages):
                return False
            return not any(record["name"].startswith(prefix) for prefix in prefixes)

        return filter_func

    # TODO: need to figure this out.
    def _should_log_to_console(self, record) -> bool:
        """Filter function to only log to Rich when console is not in live mode."""
        try:
            return not self.app["console"].is_live()
        except KeyError, AttributeError:
            # Console not available yet, allow logging
            return True

    def __getattr__(self, name: str):
        """Proxy unknown method calls to the underlying Loguru logger."""
        return getattr(self.log, name)
