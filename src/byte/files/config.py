from typing import List

from pydantic import BaseModel, Field


class WatchConfig(BaseModel):
    enable: bool = Field(
        default=False,
        description="Enable file watching for AI comment markers (AI:, AI@, AI?, AI!). When enabled, Byte automatically detects changes and processes AI instructions.",
    )


class FilesConfig(BaseModel):
    watch: WatchConfig = WatchConfig()
    ignore: List[str] = Field(
        default=[
            ".byte/cache",
            ".ruff_cache",
            ".idea",
            ".venv",
            ".env",
            ".git",
            ".pytest_cache",
            "__pycache__",
            "node_modules",
            "dist",
        ],
        description="List of gitignore-style patterns to exclude from file discovery. Patterns support wildcards and are combined with .gitignore rules.",
    )
