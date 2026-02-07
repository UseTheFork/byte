from __future__ import annotations

import html

from byte import Service
from byte.agent import BaseState
from byte.parsing import ConventionParsingService
from byte.support import ArrayStore, Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text


class ConventionContextService(Service):
    """Service for loading and managing project conventions from markdown files.

    Uses ArrayStore to manage convention documents loaded from the conventions
    directory. Conventions are automatically loaded during boot and injected
    into the prompt context.
    Usage: `service = ConventionContextService(container)`
    """

    def boot(self) -> None:
        """Load convention files from the conventions directory into ArrayStore.

        Checks for a 'conventions' directory in BYTE_DIR and loads all .md files
        found there. Each file is stored in the ArrayStore with its filename as the key.
        Usage: `await service.boot()`
        """
        self.conventions = ArrayStore()
        self.refresh()

    def refresh(self) -> None:
        """Reload convention files from the conventions directory.

        Usage: `service.refresh()`
        """
        conventions_dir = self.app["path.conventions"]

        if not conventions_dir.exists() or not conventions_dir.is_dir():
            return

        # Iterate over conventions directory and subdirectories
        convention_parsing_service = self.app.make(ConventionParsingService)

        for md_file in sorted(conventions_dir.rglob("*.md")):
            # Parse the convention properties from the markdown file
            properties = convention_parsing_service.read_properties(md_file)

            # Store ConventionProperties keyed by name
            self.conventions.add(properties.name, properties)

    def add_convention(self, filename: str) -> ConventionContextService:
        """Add a convention document to the store by loading it from the conventions directory.

        Usage: `service.add_convention("style_guide.md")`
        """
        md_file = self.app.conventions_path(filename)

        if not md_file.exists() or not md_file.is_file():
            return self

        try:
            convention_parsing_service = self.app.make(ConventionParsingService)
            properties = convention_parsing_service.read_properties(md_file)
            self.conventions.add(properties.name, properties)
        except Exception:
            pass

        return self

    def drop_convention(self, key: str) -> ConventionContextService:
        """Remove a convention document from the store.

        Usage: `service.drop_convention("old_style_guide")`
        """
        self.conventions.remove(key)
        return self

    def clear_conventions(self) -> ConventionContextService:
        """Clear all convention documents from the store.

        Usage: `service.clear_conventions()`
        """
        self.conventions.set({})
        return self

    def get_conventions(self) -> dict[str, str]:
        """Get all convention documents from the store.

        Returns a dictionary mapping convention filenames to their formatted content.
        Usage: `conventions = service.get_conventions()`
        """
        return self.conventions.all()

    async def get_available_conventions(self, state: BaseState) -> str:
        lines = []
        if self.conventions.is_not_empty():
            lines = [Boundary.open(BoundaryType.AVAILABLE_CONVENTIONS)]
            lines.append(
                Boundary.notice(
                    f"Use the **load_conventions** tool and the **{Boundary.open(BoundaryType.LOCATION)}** to load a {BoundaryType.CONVENTION}."
                )
            )

            for convention_props in self.conventions.all().values():
                convention_location = self.app.conventions_path(convention_props.filename())

                lines.append(
                    list_to_multiline_text(
                        [
                            Boundary.open(BoundaryType.CONVENTION),
                            Boundary.open(BoundaryType.NAME),
                            html.escape(convention_props.name),
                            Boundary.close(BoundaryType.NAME),
                            Boundary.open(BoundaryType.DESCRIPTION),
                            html.escape(convention_props.description),
                            Boundary.close(BoundaryType.DESCRIPTION),
                            Boundary.open(BoundaryType.LOCATION),
                            html.escape(str(convention_location)),
                            Boundary.close(BoundaryType.LOCATION),
                            Boundary.close(BoundaryType.CONVENTION),
                        ]
                    )
                )
            lines.append(Boundary.close(BoundaryType.AVAILABLE_CONVENTIONS))

        formatted_conventions = list_to_multiline_text(lines)

        return formatted_conventions
