from byte.core.array_store import ArrayStore
from byte.core.event_bus import Payload
from byte.core.service.base_service import Service
from byte.core.utils import list_to_multiline_text
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary


class ConventionContextService(Service):
    """Service for loading and managing project conventions from markdown files.

    Uses ArrayStore to manage convention documents loaded from the conventions
    directory. Conventions are automatically loaded during boot and injected
    into the prompt context.
    Usage: `service = ConventionContextService(container)`
    """

    async def boot(self) -> None:
        """Load convention files from the conventions directory into ArrayStore.

        Checks for a 'conventions' directory in BYTE_DIR and loads all .md files
        found there. Each file is stored in the ArrayStore with its filename as the key.
        Usage: `await service.boot()`
        """
        self.conventions = ArrayStore()
        conventions_dir = self._config.system.paths.conventions

        if not conventions_dir.exists() or not conventions_dir.is_dir():
            return

        # Iterate over all .md files in the conventions directory
        for md_file in sorted(conventions_dir.glob(pattern="*.md", case_sensitive=False)):
            try:
                content = md_file.read_text(encoding="utf-8")
                # Format as a document with filename header and separator
                formatted_doc = list_to_multiline_text(
                    [
                        Boundary.open(
                            BoundaryType.CONVENTION,
                            meta={"title": md_file.name.title(), "source": str(md_file)},
                        ),
                        "```markdown",
                        content,
                        "```",
                        Boundary.close(BoundaryType.CONVENTION),
                    ]
                )
                self.conventions.add(md_file.name, formatted_doc)
            except Exception:
                pass

    async def add_project_context_hook(self, payload: Payload) -> Payload:
        if self.conventions.is_not_empty():
            conventions = "\n\n".join(self.conventions.all().values())

            # Get existing list and append
            conventions_list = payload.get("conventions", [])
            conventions_list.append(conventions)
            payload.set("conventions", conventions_list)

        return payload
