from pathlib import Path

from pydantic import Field

from byte.core.config.config import BaseConfig


class MemoryConfig(BaseConfig):
    """Memory domain configuration for conversation persistence."""

    database_path: Path = Field(default_factory=lambda: Path(".byte/memory.db"))
    thread_retention_days: int = 30  # How long to keep conversation threads
    max_threads_per_user: int = 100  # Maximum threads before cleanup
    enable_compression: bool = True  # Compress old conversation data
