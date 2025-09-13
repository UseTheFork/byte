from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MemoryConfig:
    """Memory domain configuration for conversation persistence."""

    database_path: Optional[str] = None  # Defaults to .byte/memory.db
    thread_retention_days: int = 30  # How long to keep conversation threads
    max_threads_per_user: int = 100  # Maximum threads before cleanup
    enable_compression: bool = True  # Compress old conversation data
