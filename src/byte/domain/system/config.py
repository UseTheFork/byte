from pydantic import BaseModel, Field


class SystemConfig(BaseModel):
	version: str = Field(
		default="dev",
		description="List of gitignore-style patterns to exclude from file discovery. Patterns support wildcards and are combined with .gitignore rules.",
	)
