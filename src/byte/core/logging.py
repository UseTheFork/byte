import logging
from pathlib import Path

from rich.traceback import install

# Set rich as the default traceback handler
install(show_locals=True)


def _get_log_file_path() -> Path:
    """Get the log file path from BYTE_CACHE_DIR.

    Imports config locally to avoid circular dependency issues.
    Usage: `log_path = _get_log_file_path()`
    """
    from byte.core.config.config import BYTE_CACHE_DIR

    return BYTE_CACHE_DIR / "byte.log"


# Clear log file on boot by opening in write mode
LOG_FILE = _get_log_file_path()
LOG_FILE.write_text("")

# Configure file handler to append to the now-empty log file
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# Basic logging config with both handlers
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler],
    datefmt="[%X]",
)

# Create application logger
log = logging.getLogger("byte")

# Disable noisy third-party loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
