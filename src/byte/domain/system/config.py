from pathlib import Path

from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    cache: Path = Field(default=Path(), description="Path to cache directory", exclude=True)
    session_context: Path = Field(default=Path(), description="Path to session context directory", exclude=True)
    conventions: Path = Field(default=Path(), description="Path to conventions directory", exclude=True)


class SystemConfig(BaseModel):
    paths: PathsConfig = Field(default_factory=PathsConfig, description="System paths configuration")
    version: str = Field(
        default="dev",
        description="List of gitignore-style patterns to exclude from file discovery. Patterns support wildcards and are combined with .gitignore rules.",
        exclude=True,
    )
