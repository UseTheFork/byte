from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Skill:
    """Represents a parsed SKILL.md file.

    Attributes:
        name: Unique skill name (from frontmatter).
        description: Short description of the skill (from frontmatter).
        instructions: Body content of the skill file (after frontmatter).
        path: Directory containing the SKILL.md file.
        skill_file_path: Absolute path to the SKILL.md file.
        builtin: True if this skill was loaded from the Byte builtin skills directory.
        version: Optional version string (from frontmatter).
    """

    name: str
    description: str
    instructions: str
    path: Path
    skill_file_path: Path
    builtin: bool = False
    version: Optional[str] = None
