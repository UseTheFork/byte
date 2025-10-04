import logging

from rich.logging import RichHandler
from rich.traceback import install

# Set rich as the default traceback handler
install(show_locals=True)

FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

# Create your application logger and set it to DEBUG
log = logging.getLogger("byte")
log.setLevel(logging.DEBUG)

# Optional: If you want to be more explicit, you can also disable specific noisy loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)
logging.getLogger("pydoll").setLevel(logging.WARNING)
