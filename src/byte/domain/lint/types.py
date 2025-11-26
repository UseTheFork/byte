from pathlib import Path
from typing import List

from pydantic.dataclasses import dataclass


@dataclass
class LintFile:
    """Dataclass representing the result of executing a lint command on a specific file."""

    file: Path
    full_command: str
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""


@dataclass
class LintCommand:
    """Dataclass representing a lint command with results for multiple files."""

    command: List[str]
    results: List[LintFile]
