from pathlib import Path

from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
	"""Memory domain configuration for conversation persistence."""

	database_path: Path = Field(default=Path("memory.db"))
	thread_retention_days: int = 30  # How long to keep conversation threads
	enable_compression: bool = True  # Compress old conversation data
