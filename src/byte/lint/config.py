from typing import List

from pydantic import BaseModel, Field


class LintCommandConfig(BaseModel):
    command: List[str] = Field(
        description="Command and arguments to execute for linting (e.g., ['ruff', 'check', '--fix']). Use {files} placeholder to specify where the file paths should be inserted, otherwise they will be appended to the end."
    )
    languages: List[str] = Field(
        description="List of language names this command handles (e.g., ['python', 'php']). Empty list means all files."
    )


class LintConfig(BaseModel):
    """Lint domain configuration with validation and defaults."""

    enable: bool = Field(default=False, description="Enable or disable the linting functionality")
    commands: List[LintCommandConfig] = Field(
        default=[], description="List of lint commands to run on files with their target extensions"
    )
