from typing import Literal

from byte.support import Boundary, BoundaryType
from byte.support.mixins import Bootable
from byte.support.utils import list_to_multiline_text, slugify


class SessionContextModel(Bootable):
    """Model representing a session context item with file-based persistence.

    Content is stored in .byte/session_context/ and loaded on-demand.
    Similar to FileContext pattern for consistent file handling.
    """

    def boot(self, type: Literal["web", "file", "agent"], key: str, **kwargs) -> None:
        self.type = type
        self.key = key

        self.file_path = self.app.session_context_path(f"{slugify(self.key)}.md")
        self.set_content(kwargs.get("content"))

    @property
    def content(self) -> str:
        """Read content from file, returning empty string if unreadable.

        Usage: `text = model.content`
        """
        try:
            return self.file_path.read_text(encoding="utf-8")
        except FileNotFoundError, PermissionError, UnicodeDecodeError:
            return ""

    def set_content(self, content: str) -> None:
        """Write content to file, creating parent directories if needed.

        Usage: `model.set_content("New content here")`
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(content, encoding="utf-8")

    def exists(self) -> bool:
        """Check if the content file exists.

        Usage: `if model.exists(): ...`
        """
        return self.file_path.exists()

    def delete(self) -> None:
        """Delete the content file if it exists.

        Usage: `model.delete()`
        """
        if self.file_path.exists():
            self.file_path.unlink()

    def to_boundary(self) -> str:
        opening = Boundary.open(
            BoundaryType.CONTEXT,
            meta={"type": self.type, "key": self.key},
        )
        content = str(self.content)
        closing = Boundary.close(BoundaryType.CONTEXT)
        return list_to_multiline_text(
            [
                opening,
                content,
                closing,
            ]
        )
