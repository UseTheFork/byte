from typing import List

from byte.core.config.config import BYTE_DIR
from byte.core.service.base_service import Service


class ConventionsService(Service):
    """Service for loading and managing project conventions from markdown files."""

    conventions: List[str] = []

    async def boot(self) -> None:
        """Load convention files from the conventions directory.

        Checks for a 'conventions' directory in BYTE_DIR and loads all .md files
        found there. Each file is formatted as a document with its filename as a header.
        """
        conventions_dir = BYTE_DIR / "conventions"

        if not conventions_dir.exists() or not conventions_dir.is_dir():
            return

        self.conventions = []

        # Iterate over all .md files in the conventions directory
        for md_file in sorted(conventions_dir.glob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
                # Format as a document with filename header and separator
                formatted_doc = f"---\n\n# Convention: {md_file.name}\n\n{content}"
                self.conventions.append(formatted_doc)
            except Exception:
                pass
