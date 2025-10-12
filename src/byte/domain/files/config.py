from typing import List

from pydantic import BaseModel, Field


class WatchConfig(BaseModel):
	enable: bool = True


class FilesConfig(BaseModel):
	watch: WatchConfig = WatchConfig()
	ignore: List[str] = Field(
		default=[],
		description="List of gitignore-style patterns to exclude from file discovery. Patterns support wildcards and are combined with .gitignore rules.",
	)
