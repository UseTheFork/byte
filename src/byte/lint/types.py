from pathlib import Path
from typing import List

from pydantic.dataclasses import dataclass


@dataclass
class LintTask:
    """Dataclass representing a lint command with multiple files to process."""

    command: List[str]
    files: List[Path]
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
