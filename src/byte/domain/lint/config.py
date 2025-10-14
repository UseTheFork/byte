from typing import List

from pydantic import BaseModel, Field


class LintCommand(BaseModel):
	command: str = Field(description="Shell command to execute for linting (e.g., 'ruff check --fix')")
	extensions: List[str] = Field(
		description="List of file extensions to run this command on (e.g., ['.py', '.pyi']). Empty list means all files."
	)


class LintConfig(BaseModel):
	"""Lint domain configuration with validation and defaults."""

	enable: bool = Field(default=True, description="Enable or disable the linting functionality")
	commands: List[LintCommand] = Field(
		default=[], description="List of lint commands to run on files with their target extensions"
	)
