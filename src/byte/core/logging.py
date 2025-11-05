from pathlib import Path

from loguru import logger


def _get_log_file_path() -> Path:
    """Get the log file path from BYTE_CACHE_DIR.

    Imports config locally to avoid circular dependency issues.
    Usage: `log_path = _get_log_file_path()`
    """
    from byte.core.config.config import BYTE_CACHE_DIR

    return BYTE_CACHE_DIR / "byte.log"


# Clear log files on boot
LOG_FILE = _get_log_file_path()
LOG_FILE.write_text("")


config = {
    "handlers": [
        {"sink": LOG_FILE, "level": "DEBUG", "serialize": False, "backtrace": True},
    ],
}
logger.configure(**config)


log = logger
