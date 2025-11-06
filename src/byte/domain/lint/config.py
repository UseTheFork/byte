from typing import List

from pydantic import BaseModel, Field


class LintCommand(BaseModel):
    command: List[str] = Field(
        description="Command and arguments to execute for linting (e.g., ['ruff', 'check', '--fix'])"
    )
    languages: List[str] = Field(
        description="List of language names this command handles (e.g., ['python', 'php']). Empty list means all files."
    )


class LintConfig(BaseModel):
    """Lint domain configuration with validation and defaults."""

    enable: bool = Field(default=False, description="Enable or disable the linting functionality")
    commands: List[LintCommand] = Field(
        default=[], description="List of lint commands to run on files with their target extensions"
    )
