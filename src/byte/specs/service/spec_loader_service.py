import json
import re
from pathlib import Path
from typing import Optional

from byte import Service
from byte.specs.schemas import Spec, SpecPhase

SPEC_FILE_NAME = "SPEC.md"
PHASES_FILE_NAME = "phases.json"
FRONTMATTER_PATTERN = re.compile(r"^---[\r\n]+(.*?)[\r\n]+---", re.DOTALL | re.MULTILINE)


class SpecLoaderService(Service):
    """Service for discovering and loading specs from the specs directory.

    Scans ``app.specs_path()`` (.byte/specs) for subdirectories each containing
    a ``SPEC.md`` file with YAML frontmatter, parsed into
    :class:`~byte.specs.schemas.Spec` instances.

    Usage:
        spec_loader = app.make(SpecLoaderService)
        specs = spec_loader.specs          # dict of active Spec objects keyed by name
        spec_loader.reload()               # re-scan the specs directory
    """

    def boot(self) -> None:
        """Discover and load specs on service initialization.

        Usage: Called automatically when the service is resolved from the container.
        """
        self._specs: dict[str, Spec] = {}
        self.reload()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def specs(self) -> dict[str, Spec]:
        """Return the current dict of loaded specs, keyed by name.

        Usage: `for name, spec in service.specs.items(): ...`
        """
        return dict(self._specs)

    def get_spec(self, name: str) -> Optional[Spec]:
        """Return a spec by name, or None if not found.

        Args:
            name: The spec name to look up.

        Usage: `spec = service.get_spec("my-feature")`
        """
        return self._specs.get(name)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_spec_files(self, directory: Path) -> list[Path]:
        """Find all ``SPEC.md`` files that are direct children of a subdirectory under *directory*.

        Each spec lives in its own subdirectory as ``<topic>/SPEC.md``.
        Performs case-insensitive matching so ``spec.md`` and ``Spec.MD`` are
        also discovered on case-sensitive filesystems.

        Args:
            directory: Root directory to search.

        Returns:
            List of absolute paths to SPEC.md files.
        """
        found: list[Path] = []
        try:
            for item in directory.rglob("*"):
                if item.is_file() and item.name.upper() == SPEC_FILE_NAME.upper():
                    found.append(item.resolve())
        except PermissionError:
            self.app["log"].warning(f"Permission denied scanning: {directory}")
        except OSError as exc:
            self.app["log"].warning(f"Error scanning directory {directory}: {exc}")
        return found

    def _parse_spec_file(self, spec_file: Path) -> Optional[Spec]:
        """Parse a single ``SPEC.md`` file into a Spec dataclass.

        Reads YAML frontmatter for *name*, *description*, *version*, and
        *tags*, treating the remainder of the file as the spec instructions.

        Args:
            spec_file: Absolute path to the spec file.

        Returns:
            A populated Spec instance, or None if parsing fails.
        """
        try:
            content = spec_file.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            self.app["log"].warning(f"Could not read spec file {spec_file}: {exc}")
            return None

        match = FRONTMATTER_PATTERN.match(content)
        if not match:
            self.app["log"].warning(f"No YAML frontmatter found in {spec_file}, skipping")
            return None

        frontmatter_text = match.group(1)
        body = content[match.end() :].strip()

        try:
            import yaml  # lazy import — yaml is an optional dep at module level

            frontmatter = yaml.safe_load(frontmatter_text)
        except Exception as exc:
            self.app["log"].warning(f"Failed to parse YAML frontmatter in {spec_file}: {exc}")
            return None

        if not isinstance(frontmatter, dict):
            self.app["log"].warning(f"Frontmatter in {spec_file} is not a mapping, skipping")
            return None

        name = frontmatter.get("name")
        description = frontmatter.get("description")

        if not name or not isinstance(name, str):
            self.app["log"].warning(f"Missing or invalid 'name' in {spec_file}, skipping")
            return None

        if not description or not isinstance(description, str):
            self.app["log"].warning(f"Missing or invalid 'description' in {spec_file}, skipping")
            return None

        version = frontmatter.get("version")
        if version is not None and not isinstance(version, str):
            version = str(version)

        tags = frontmatter.get("tags")
        if tags is not None and not isinstance(tags, list):
            self.app["log"].warning(f"'tags' in {spec_file} is not a list, ignoring")
            tags = None

        return Spec(
            name=name.strip(),
            description=description.strip(),
            instructions=body,
            path=spec_file.parent,
            spec_file_path=spec_file,
            version=version.strip() if isinstance(version, str) else None,
            tags=tags,
        )

    def _load_from_directory(self, directory: Path) -> dict[str, Spec]:
        """Scan *directory* for spec subdirectories each containing a ``SPEC.md`` file and parse each one.

        Args:
            directory: Root directory to scan.

        Returns:
            Dict of successfully parsed Spec objects keyed by name (empty if dir missing).
        """
        if not directory.exists():
            self.app["log"].debug(f"Specs directory does not exist, skipping: {directory}")
            return {}

        if not directory.is_dir():
            self.app["log"].warning(f"Specs path is not a directory, skipping: {directory}")
            return {}

        specs: dict[str, Spec] = {}

        for spec_file in self._find_spec_files(directory):
            spec = self._parse_spec_file(spec_file)
            if spec is not None:
                specs[spec.name] = spec

        self.app["log"].debug(f"Found {len(specs)} spec(s) in {directory}")
        return specs

    def load_phases(self, spec_name: str) -> list[SpecPhase]:
        """Load phases for a spec from its ``phases.json`` file.

        Returns an empty list if the spec does not exist or no phases file is present.

        Args:
            spec_name: The name of the spec to load phases for.

        Usage: `phases = service.load_phases("my-feature")`
        """
        spec = self.get_spec(spec_name)
        if spec is None:
            return []

        phases_file = spec.path / PHASES_FILE_NAME
        if not phases_file.exists():
            return []

        try:
            raw = json.loads(phases_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.app["log"].warning(f"Could not read phases file {phases_file}: {exc}")
            return []

        phases: list[SpecPhase] = []
        for item in raw:
            try:
                phases.append(
                    SpecPhase(
                        id=item["id"],
                        status=item.get("status", "pending"),
                        content=item.get("content", ""),
                        notes=item.get("notes", []),
                    )
                )
            except (KeyError, TypeError) as exc:
                self.app["log"].warning(f"Skipping malformed phase entry in {phases_file}: {exc}")

        return phases

    def save_phases(self, spec_name: str, phases: list[SpecPhase]) -> bool:
        """Persist *phases* for a spec as ``phases.json`` alongside its ``SPEC.md``.

        Args:
            spec_name: The name of the spec to save phases for.
            phases: The list of :class:`~byte.specs.schemas.SpecPhase` objects to persist.

        Returns:
            ``True`` if the file was written successfully, ``False`` otherwise.

        Usage: `service.save_phases("my-feature", phases)`
        """
        spec = self.get_spec(spec_name)
        if spec is None:
            self.app["log"].warning(f"Cannot save phases — spec '{spec_name}' not found")
            return False

        phases_file = spec.path / PHASES_FILE_NAME
        payload = [
            {
                "id": phase.id,
                "status": phase.status,
                "content": phase.content,
                "notes": phase.notes,
            }
            for phase in phases
        ]

        try:
            phases_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError as exc:
            self.app["log"].warning(f"Could not write phases file {phases_file}: {exc}")
            return False

        return True

    def reload(self, *args) -> None:
        """Re-scan the specs directory and refresh the loaded specs dict.

        Usage: `service.reload()`
        """
        specs_dir = self.app.specs_path()
        self._specs = self._load_from_directory(specs_dir)

        self.app["log"].debug(f"SpecLoaderService loaded {len(self._specs)} spec(s)")
