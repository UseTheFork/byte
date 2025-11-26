from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from byte.core.utils import get_language_from_filename


class FileMode(Enum):
    """File access mode for AI context management."""

    READ_ONLY = "read_only"
    EDITABLE = "editable"


class FileContext(BaseModel):
    """Immutable file context containing path and access mode information."""

    path: Path
    mode: FileMode

    @property
    def language(self) -> str:
        """Get the programming language of the file based on its filename.

        Usage: `file_context.language` -> 'Python' or 'text'
        """
        return get_language_from_filename(str(self.path)) or "text"

    @property
    def relative_path(self) -> str:
        """Get relative path string for display purposes."""
        try:
            # Try to get relative path from current working directory
            return str(self.path.relative_to(Path.cwd()))
        except ValueError:
            # If path is outside cwd, return absolute path
            return str(self.path)

    def get_content(self) -> Optional[str]:
        """Read file content safely, returning None if unreadable."""
        try:
            return self.path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            return None
