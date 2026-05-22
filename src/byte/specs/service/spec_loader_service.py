import re
from pathlib import Path
from typing import Optional

from byte import Service
from byte.specs import SpecTask
from byte.specs.schemas import Spec, SpecTaskFiles
from byte.support.yaml import Yaml

SPEC_FILE_NAME = "SPEC.md"
TASKS_DIR_NAME = "tasks"


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

        try:
            frontmatter, body = Yaml.parse_frontmatter(content)
        except Exception as exc:
            self.app["log"].warning(f"Failed to parse frontmatter in {spec_file}: {exc}")
            return None

        if not frontmatter:
            self.app["log"].warning(f"No YAML frontmatter found in {spec_file}, skipping")
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
            id=re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-"),
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
            Dict of successfully parsed Spec objects keyed by id (empty if dir missing).
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
                specs[spec.id] = spec

        self.app["log"].debug(f"Found {len(specs)} spec(s) in {directory}")
        return specs

    def _parse_task_file(self, task_file: Path) -> Optional[SpecTask]:
        """Parse a single task markdown file with YAML frontmatter.

        Reads YAML frontmatter for *id*, *order*, *status*, and *notes*,
        treating the remainder of the file as the task content.

        Args:
            task_file: Absolute path to the task markdown file.

        Returns:
            A populated Spectask instance, or None if parsing fails.
        """
        try:
            content = task_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self.app["log"].warning(f"Could not read task file {task_file}: {exc}")
            return None

        try:
            frontmatter, body = Yaml.parse_frontmatter(content)
        except Exception as exc:
            self.app["log"].warning(f"Failed to parse frontmatter in {task_file}: {exc}")
            return None

        task_id = frontmatter.get("id")
        if not task_id or not isinstance(task_id, str):
            self.app["log"].warning(f"Missing or invalid 'id' in {task_file}, skipping")
            return None

        order = frontmatter.get("order", 0)
        if not isinstance(order, int):
            try:
                order = int(order)
            except ValueError, TypeError:
                order = 0

        status = frontmatter.get("status", "pending")
        if status not in ("pending", "in_progress", "blocked", "completed"):
            status = "pending"

        notes = frontmatter.get("notes", [])
        if not isinstance(notes, list):
            notes = []

        files_data = frontmatter.get("files", {})
        if not isinstance(files_data, dict):
            files_data = {}

        files = SpecTaskFiles(
            reference=files_data.get("reference", []) if isinstance(files_data.get("reference"), list) else [],
            create=files_data.get("create", []) if isinstance(files_data.get("create"), list) else [],
            edit=files_data.get("edit", []) if isinstance(files_data.get("edit"), list) else [],
        )

        return SpecTask(
            id=task_id,
            order=order,
            status=status,
            content=body,
            notes=notes,
            files=files,
        )

    def load_tasks(self, spec_name: str) -> list[SpecTask]:
        """Load tasks for a spec from its ``tasks/`` subdirectory.

        tasks are stored as individual markdown files with YAML frontmatter.
        Returns an empty list if the spec does not exist or no tasks directory is present.

        Args:
            spec_name: The name of the spec to load tasks for.

        Usage: `tasks = service.load_tasks("my-feature")`
        """
        spec = self.get_spec(spec_name)
        if spec is None:
            return []

        tasks_dir = spec.path / TASKS_DIR_NAME
        if not tasks_dir.exists():
            return []

        tasks: list[SpecTask] = []
        try:
            for task_file in sorted(tasks_dir.glob("*.md")):
                task = self._parse_task_file(task_file)
                if task is not None:
                    tasks.append(task)
        except (OSError, PermissionError) as exc:
            self.app["log"].warning(f"Could not scan tasks directory {tasks_dir}: {exc}")
            return []

        # Sort by order field
        tasks.sort(key=lambda p: (p.order, p.id))
        return tasks

    def save_tasks(self, spec_name: str, tasks: list[SpecTask]) -> bool:
        """Persist *tasks* for a spec as individual markdown files in ``tasks/`` subdirectory.

        Each task is saved with YAML frontmatter containing id, order, status, and notes,
        followed by the task content. File names are normalized task IDs.

        Args:
            spec_name: The name of the spec to save tasks for.
            tasks: The list of :class:`~byte.specs.schemas.Spectask` objects to persist.

        Returns:
            ``True`` if all tasks were written successfully, ``False`` if any write failed.

        Usage: `service.save_tasks("my-feature", tasks)`
        """
        spec = self.get_spec(spec_name)
        if spec is None:
            self.app["log"].warning(f"Cannot save tasks — spec '{spec_name}' not found")
            return False

        tasks_dir = spec.path / TASKS_DIR_NAME
        try:
            tasks_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.app["log"].warning(f"Could not create tasks directory {tasks_dir}: {exc}")
            return False

        all_success = True
        for task in tasks:
            # Normalize task id to filename (convert to lowercase, replace spaces/hyphens)
            normalized_id = re.sub(r"[^a-z0-9]+", "-", task.id.lower()).strip("-")
            task_file = tasks_dir / f"{normalized_id}.md"

            frontmatter = {
                "id": task.id,
                "order": task.order,
                "status": task.status,
                "notes": task.notes,
                "files": {
                    "reference": task.files.reference,
                    "create": task.files.create,
                    "edit": task.files.edit,
                },
            }

            content = Yaml.render_frontmatter(frontmatter, task.content)

            try:
                task_file.write_text(content, encoding="utf-8")
            except OSError as exc:
                self.app["log"].warning(f"Could not write task file {task_file}: {exc}")
                all_success = False

        return all_success

    def save_task(self, spec_name: str, task: SpecTask) -> bool:
        """Persist a single *task* for a spec as a markdown file in the ``tasks/`` subdirectory.

        The task is saved with YAML frontmatter containing id, order, status, and notes,
        followed by the task content. File name is the normalized task ID.

        Args:
            spec_name: The name of the spec to save the task for.
            task: The :class:`~byte.specs.schemas.SpecTask` object to persist.

        Returns:
            ``True`` if the task was written successfully, ``False`` otherwise.

        Usage: `service.save_task("my-feature", task)`
        """
        spec = self.get_spec(spec_name)
        if spec is None:
            self.app["log"].warning(f"Cannot save task — spec '{spec_name}' not found")
            return False

        tasks_dir = spec.path / TASKS_DIR_NAME
        try:
            tasks_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.app["log"].warning(f"Could not create tasks directory {tasks_dir}: {exc}")
            return False

        normalized_id = re.sub(r"[^a-z0-9]+", "-", task.id.lower()).strip("-")
        task_file = tasks_dir / f"{normalized_id}.md"

        frontmatter = {
            "id": task.id,
            "order": task.order,
            "status": task.status,
            "notes": task.notes,
            "files": {
                "reference": task.files.reference,
                "create": task.files.create,
                "edit": task.files.edit,
            },
        }

        content = Yaml.render_frontmatter(frontmatter, task.content)

        try:
            task_file.write_text(content, encoding="utf-8")
            return True
        except OSError as exc:
            self.app["log"].warning(f"Could not write task file {task_file}: {exc}")
            return False

    def reload(self, *args) -> None:
        """Re-scan the specs directory and refresh the loaded specs dict.

        Usage: `service.reload()`
        """
        specs_dir = self.app.specs_path()
        self._specs = self._load_from_directory(specs_dir)

        self.app["log"].debug(f"SpecLoaderService loaded {len(self._specs)} spec(s)")
