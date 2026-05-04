import re
from pathlib import Path
from typing import Optional

from byte import Service
from byte.skills.schemas import Skill
from byte.support.boundary import Boundary, BoundaryType

SKILL_FILE_NAME = "SKILL.md"
FRONTMATTER_PATTERN = re.compile(r"^---[\r\n]+(.*?)[\r\n]+---", re.DOTALL | re.MULTILINE)


class SkillLoaderService(Service):
    """Service for discovering and loading skills from multiple source directories.

    Scans the following paths in priority order (lowest to highest):
      1. Byte builtin skills (shipped with the package)
      2. app.root_path(".agent/skills") — agent-level user skills
      3. app.skills_path()              — project-level user skills (.byte/skills)

    When two skills share the same name the higher-priority source wins, so
    project skills override agent skills, and both override builtins — matching
    the deduplication strategy used by Crush.

    Usage:
        skill_loader = app.make(SkillLoaderService)
        skills = skill_loader.skills          # list of active Skill objects
        skill_loader.reload()                 # re-scan all paths
    """

    def boot(self) -> None:
        """Discover and load skills on service initialisation.

        Usage: `service = SkillLoaderService(container)` — boot is called automatically.
        """
        self._skills: dict[str, Skill] = {}
        self.reload()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def skills(self) -> dict[str, Skill]:
        """Return the current dict of active (deduplicated) skills, keyed by name.

        Usage: `for name, skill in service.skills.items(): ...`
        """
        return {name: skill for name, skill in self._skills.items()}

    def get_skill(self, name: str) -> Optional[Skill]:
        """Return a skill by name, or None if not found.

        Args:
            name: The skill name to look up.

        Usage: `skill = service.get_skill("code-reviewer")`
        """
        return self._skills.get(name)

    def skills_to_prompt_xml(self, skills: Optional[dict[str, Skill]] = None) -> str:
        """Format a dict of skills as XML for injection into a system prompt.

        Args:
            skills: Skills to format. Defaults to the current active skills dict.

        Returns:
            An XML string wrapped in ``<available_skills>`` tags, or an empty
            string if there are no skills to render.

        Usage: `xml = service.skills_to_prompt_xml()`
        Usage: `xml = service.skills_to_prompt_xml(my_skills)`
        """
        if skills is None:
            skills = self._skills

        if not skills:
            return ""

        lines: list[str] = [Boundary.open(BoundaryType.AVAILABLE_SKILLS)]
        for skill in skills.values():
            lines.append(f"  {Boundary.open(BoundaryType.SKILL)}")
            lines.append(f"    {Boundary.open(BoundaryType.NAME)}{skill.name}{Boundary.close(BoundaryType.NAME)}")
            lines.append(
                f"    {Boundary.open(BoundaryType.DESCRIPTION)}{skill.description}{Boundary.close(BoundaryType.DESCRIPTION)}"
            )
            lines.append(
                f"    {Boundary.open(BoundaryType.LOCATION)}{skill.skill_file_path}{Boundary.close(BoundaryType.LOCATION)}"
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

        match = FRONTMATTER_PATTERN.match(content)
        if not match:
            self.app["log"].warning(f"No YAML frontmatter found in {skill_file}, skipping")
            return None

        frontmatter_text = match.group(1)
        body = content[match.end() :].strip()

        try:
            import yaml  # lazy import — yaml is an optional dep at module level

            frontmatter = yaml.safe_load(frontmatter_text)
        except Exception as exc:
            self.app["log"].warning(f"Failed to parse YAML frontmatter in {skill_file}: {exc}")
            return None

        if not isinstance(frontmatter, dict):
            self.app["log"].warning(f"Frontmatter in {skill_file} is not a mapping, skipping")
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

        metadata = frontmatter.get("metadata")
        allowed_tools = None
        if isinstance(metadata, dict):
            allowed_tools = metadata.get("allowed-tools")
            if allowed_tools is not None and not isinstance(allowed_tools, list):
                self.app["log"].warning(f"'allowed-tools' in metadata of {skill_file} is not a list, ignoring")
                allowed_tools = None

        return Skill(
            name=name.strip(),
            description=description.strip(),
            instructions=body,
            path=skill_file.parent,
            skill_file_path=skill_file,
            builtin=builtin,
            allowed_tools=allowed_tools,
            version=version.strip() if isinstance(version, str) else None,
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
            Dict of successfully parsed Skill objects keyed by name (empty if dir missing).
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
                skills[skill.name] = skill

        self.app["log"].debug(f"Found {len(skills)} skill(s) in {directory}")
        return skills

    def reload(self, *args) -> None:
        """Re-scan all skill directories and refresh the active skills dict.

        Collects skills from all sources in ascending priority order so that
        higher-priority (user) skills override lower-priority (builtin) ones.

        Usage: `service.reload()`
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
