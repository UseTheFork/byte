from typing import List

from pydantic import BaseModel


class LintCommand(BaseModel):
	command: str
	extensions: List[str]


class LintConfig(BaseModel):
	"""Lint domain configuration with validation and defaults."""

	enable: bool = True
	commands: List[LintCommand] = []
