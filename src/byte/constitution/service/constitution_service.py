import json
from pathlib import Path
from typing import Optional

from byte import Service
from byte.constitution.models import Constitution

CONSTITUTION_FILE_NAME = "constitution.json"


class ConstitutionService(Service):
    """Service for loading and managing the project constitution.

    The constitution is persisted as a JSON file at
    ``app.config_path("constitution.json")`` and is loaded on boot.

    Usage:
        service = app.make(ConstitutionService)
        constitution = service.constitution   # access the loaded Constitution
        service.reload()                      # re-read from disk
    """

    def boot(self) -> None:
        """Initialise the service and load the constitution from disk.

        Usage: called automatically when the service provider boots.
        """
        self._constitution: Optional[Constitution] = None
        self._constitution_path: Path = self.app.config_path(CONSTITUTION_FILE_NAME)
        self.reload()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def constitution(self) -> Optional[Constitution]:
        """Return the currently loaded Constitution, or None if not found.

        Usage: `c = service.constitution`
        """
        return self._constitution

    @property
    def constitution_path(self) -> Path:
        """Return the path to the constitution JSON file.

        Usage: `path = service.constitution_path`
        """
        return self._constitution_path

    def reload(self) -> None:
        """Re-read the constitution JSON file from disk.

        Silently sets ``self._constitution`` to None if the file does not
        exist yet; logs a warning if the file exists but cannot be parsed.

        Usage: `service.reload()`
        """
        path = self._constitution_path

        if not path.exists():
            self.app["log"].debug(f"ConstitutionService: no constitution file found at {path}, creating blank constitution")
            self._constitution = self._create_blank()
            self._save(self._constitution)
            return

        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            self._constitution = Constitution.from_dict(data)
            self.app["log"].debug(
                f"ConstitutionService: loaded constitution "
                f"'{self._constitution.project_name}' "
                f"v{self._constitution.meta.version} from {path}"
            )
        except (OSError, json.JSONDecodeError) as exc:
            self.app["log"].warning(f"ConstitutionService: failed to load constitution from {path}: {exc}")
            self._constitution = None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_blank(self) -> Constitution:
        """Create a blank Constitution with sensible defaults.

        Usage: `c = self._create_blank()`
        """
        from byte.constitution.models import ConstitutionMeta, ConstitutionPrinciple

        today = __import__("datetime").date.today().isoformat()
        return Constitution(
            project_name="Untitled Constitution",
            principles=[
                ConstitutionPrinciple(
                    name="I. Example Principle",
                    description="Describe your first core principle here.",
                )
            ],
            governance="Constitution supersedes all other practices. Amendments require documentation and approval.",
            meta=ConstitutionMeta(version="0.1.0", ratified=today, last_amended=today),
            sections=[],
        )

    def _save(self, constitution: Constitution) -> None:
        """Persist *constitution* to disk as JSON.

        Creates parent directories if they do not exist.

        Usage: `self._save(constitution)`
        """
        path = self._constitution_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(constitution.to_dict(), indent=2), encoding="utf-8")
        self.app["log"].debug(f"ConstitutionService: saved constitution to {path}")
