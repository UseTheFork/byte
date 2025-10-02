from textwrap import dedent
from typing import List

from byte.core.config.config import BYTE_DIR
from byte.core.event_bus import Payload
from byte.core.service.base_service import Service


class ConventionContextService(Service):
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
                formatted_doc = f"## Convention: {md_file.name}\n\n{content}"
                self.conventions.append(formatted_doc)
            except Exception:
                pass

    async def add_project_context(self, payload: Payload) -> Payload:
        """ """

        state = payload.get("state", {})
        project_inforamtion_and_context = state.get(
            "project_inforamtion_and_context", []
        )

        conventions = "\n\n".join(self.conventions)

        project_inforamtion_and_context.append(
            (
                "user",
                dedent(f"""
                # Coding and Project Conventions

                **Important:** Adhere to the following project-specific conventions. These standards are essential for maintaining code quality and consistency.
                {conventions}
                """),
            )
        )
        state["project_inforamtion_and_context"] = project_inforamtion_and_context

        return payload.set("state", state)
