from pathlib import Path
from typing import Optional

from byte import Service
from byte.skills.schemas import Skill
from byte.support.boundary import Boundary, BoundaryType
from byte.support.string import Str
from byte.support.yaml import Yaml

SKILL_FILE_NAME = "SKILL.md"


class SkillLoaderService(Service):
    """Service for discovering and loading skills from multiple source directories.

    Scans the following paths in priority order (lowest to highest):
      1. Byte builtin skills (shipped with the package)
      2. app.root_path(".agent/skills") — agent-level user skills
      3. app.skills_path()              — project-level user skills (.byte/skills)

    When two skills share the same name the higher-priority source wins, so
    project skills override agent skills, and both override builtins — matching
    the deduplication strategy used by Crush.
    """

    def boot(self) -> None:
        """Discover and load skills on service initialization."""
        self._skills: dict[str, Skill] = {}
        self.reload()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def skills(self) -> dict[str, Skill]:
        """Return the current dict of active (deduplicated) skills, keyed by name."""
        return {name: skill for name, skill in self._skills.items()}

    def get_skill(self, name: str) -> Optional[Skill]:
        """Return a skill by name, or None if not found.

        Args:
            name: The skill name to look up.
        """
        return self._skills.get(name)

    def skills_to_prompt_xml(self, skills: Optional[dict[str, Skill]] = None) -> str:
        """Format a dict of skills as XML for injection into a system prompt.

        Args:
            skills: Skills to format. Defaults to the current active skills dict.

        Returns:
            An XML string wrapped in ``<available_skills>`` tags, or an empty
            string if there are no skills to render.
        """
        if skills is None:
            skills = self._skills

        if not skills:
            return ""

        lines: list[str] = [Boundary.open(BoundaryType.AVAILABLE_SKILLS)]
        for skill in skills.values():
            lines.append(f"  {Boundary.open(BoundaryType.SKILL)}")
            lines.append(f"    {Boundary.open(BoundaryType.ID)}{skill.id}{Boundary.close(BoundaryType.ID)}")
            lines.append(f"    {Boundary.open(BoundaryType.NAME)}{skill.name}{Boundary.close(BoundaryType.NAME)}")
            lines.append(
                f"    {Boundary.open(BoundaryType.DESCRIPTION)}{skill.description}{Boundary.close(BoundaryType.DESCRIPTION)}"
            )
            if skill.builtin:
                lines.append(f"    {Boundary.open(BoundaryType.TYPE)}builtin{Boundary.close(BoundaryType.TYPE)}")
            lines.append(f"  {Boundary.close(BoundaryType.SKILL)}")
        lines.append(Boundary.close(BoundaryType.AVAILABLE_SKILLS))

        return "\n".join(lines)

    def _find_skill_files(self, directory: Path) -> list[Path]:
        """Recursively find all SKILL.md files under *directory*.

        Performs case-insensitive matching so "skill.md" and "Skill.MD" are
        also discovered on case-sensitive filesystems.

        Args:
            directory: Root directory to search.

        Returns:
            List of absolute paths to SKILL.md files.
        """
        found: list[Path] = []
        try:
            for item in directory.rglob("*"):
                if item.is_file() and item.name.upper() == SKILL_FILE_NAME.upper():
                    found.append(item.resolve())
        except PermissionError:
            self.app["log"].warning(f"Permission denied scanning: {directory}")
        except OSError as exc:
            self.app["log"].warning(f"Error scanning directory {directory}: {exc}")
        return found

    def _parse_skill_file(self, skill_file: Path, builtin: bool = False) -> Optional[Skill]:
        """Parse a single SKILL.md file into a Skill dataclass.

        Reads YAML frontmatter for *name*, *description*, and *version*, and
        treats the remainder of the file as the skill instructions.

        Args:
            skill_file: Absolute path to the SKILL.md file.
            builtin:    Mark the resulting Skill as builtin when True.

        Returns:
            A populated Skill instance, or None if parsing fails.
        """
        try:
            content = skill_file.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            self.app["log"].warning(f"Could not read skill file {skill_file}: {exc}")
            return None

        try:
            frontmatter, body = Yaml.parse_frontmatter(content)
        except Exception as exc:
            self.app["log"].warning(f"Failed to parse frontmatter in {skill_file}: {exc}")
            return None

        if not frontmatter:
            self.app["log"].warning(f"No YAML frontmatter found in {skill_file}, skipping")
            return None

        name = frontmatter.get("name")
        description = frontmatter.get("description")

        if not name or not isinstance(name, str):
            self.app["log"].warning(f"Missing or invalid 'name' in {skill_file}, skipping")
            return None

        if not description or not isinstance(description, str):
            self.app["log"].warning(f"Missing or invalid 'description' in {skill_file}, skipping")
            return None

        version = frontmatter.get("version")
        if version is not None and not isinstance(version, str):
            version = str(version)

        references_dir = skill_file.parent / "references"
        references: dict[str, Path] = {}
        if references_dir.is_dir():
            for ref_file in sorted(references_dir.glob("*.md")):
                references[Str.normalize_id(ref_file.stem)] = ref_file.resolve()

        return Skill(
            id=Str.normalize_id(name),
            name=name.strip(),
            description=description.strip(),
            instructions=body,
            path=skill_file.parent,
            skill_file_path=skill_file,
            builtin=builtin,
            version=version.strip() if isinstance(version, str) else None,
            references=references,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_from_directory(self, directory: Path, builtin: bool = False) -> dict[str, Skill]:
        """Scan *directory* recursively for SKILL.md files and parse each one.

        Args:
            directory: Root directory to scan.
            builtin:   Mark loaded skills as builtin when True.

        Returns:
            Dict of successfully parsed Skill objects keyed by id (empty if dir missing).
        """
        if not directory.exists():
            self.app["log"].debug(f"Skills directory does not exist, skipping: {directory}")
            return {}

        if not directory.is_dir():
            self.app["log"].warning(f"Skills path is not a directory, skipping: {directory}")
            return {}

        skills: dict[str, Skill] = {}

        for skill_file in self._find_skill_files(directory):
            skill = self._parse_skill_file(skill_file, builtin=builtin)
            if skill is not None:
                skills[skill.id] = skill

        self.app["log"].debug(f"Found {len(skills)} skill(s) in {directory}")
        return skills

    def reload(self, *args) -> None:
        """Re-scan all skill directories and refresh the active skills dict.

        Collects skills from all sources in ascending priority order so that
        higher-priority (user) skills override lower-priority (builtin) ones.

        """
        merged: dict[str, Skill] = {}

        # 1. Builtin skills (lowest priority)
        builtin_dir = self.app.app_path("skills/builtin")
        merged.update(self._load_from_directory(builtin_dir, builtin=True))

        # 2. Agent-level skills — .agent/skills in the git root
        agent_skills_dir = self.app.root_path(".agent/skills")
        merged.update(self._load_from_directory(agent_skills_dir))

        # 3. Project-level skills — .byte/skills (highest priority)
        project_skills_dir = self.app.skills_path()
        merged.update(self._load_from_directory(project_skills_dir))

        self._skills = merged

        self.app["log"].debug(
            f"SkillLoaderService loaded {len(self._skills)} skill(s) "
            f"({sum(1 for s in self._skills.values() if s.builtin)} builtin)"
        )
