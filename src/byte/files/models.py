from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from byte.support import Boundary, BoundaryType
from byte.support.utils import get_language_from_filename, list_to_multiline_text


class FileContext(BaseModel):
    """Immutable file context containing path information."""

    path: Path
    root_path: Path

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
            return str(self.path.relative_to(self.root_path))
        except ValueError:
            # If path is outside cwd, return absolute path
            return str(self.path)

    def get_content(self) -> Optional[str]:
        """Read file content safely, returning None if unreadable."""
        try:
            return self.path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            return f"**ERROR** reading file:\n\n{e!s}"

    def to_boundary(self) -> str:
        opening = Boundary.open(
            BoundaryType.FILE,
            meta={"source": self.relative_path, "language": self.language},
        )
        content = str(self.get_content())
        closing = Boundary.close(BoundaryType.FILE)
        return list_to_multiline_text(
            [
                opening,
                content,
                closing,
            ]
        )

    def to_summary(self) -> Optional[str]:
        # TODO: this will use tree-sitter
        pass
