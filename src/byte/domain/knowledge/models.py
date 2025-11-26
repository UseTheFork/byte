from typing import Literal

from byte.core.mixins.bootable import Bootable
from byte.core.mixins.configurable import Configurable
from byte.core.mixins.injectable import Injectable
from byte.core.utils import slugify


class SessionContextModel(Bootable, Configurable, Injectable):
    """Model representing a session context item with file-based persistence.

    Content is stored in .byte/session_context/ and loaded on-demand.
    Similar to FileContext pattern for consistent file handling.
    """

    async def boot(self, type: Literal["web", "file", "agent"], key: str, **kwargs) -> None:
        self.type = type
        self.key = key

        self.file_path = self._config.system.paths.session_context / f"{slugify(self.key)}.md"
        self.set_content(kwargs.get("content"))

    @property
    def content(self) -> str:
        """Read content from file, returning empty string if unreadable.

        Usage: `text = model.content`
        """
        try:
            return self.file_path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
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
