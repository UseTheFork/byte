from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from byte.support import MD, Section
from byte.support.boundary import Boundary, BoundaryType


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

    id: str
    name: str
    description: str
    instructions: str
    path: Path
    skill_file_path: Path
    builtin: bool = False
    version: Optional[str] = None
    allowed_tools: Optional[list[str]] = None
    active: bool = True
    references: dict[str, Path] = field(default_factory=dict)

    def to_xml(self) -> str:
        """Convert the skill to an XML string for prompt injection."""
        lines: list[str] = []
        lines.append(f"{Boundary.open(BoundaryType.SKILL)}")
        lines.append(f"  {Boundary.open(BoundaryType.ID)}{self.id}{Boundary.close(BoundaryType.ID)}")
        lines.append(f"  {Boundary.open(BoundaryType.NAME)}{self.name}{Boundary.close(BoundaryType.NAME)}")
        lines.append(
            f"  {Boundary.open(BoundaryType.DESCRIPTION)}{self.description}{Boundary.close(BoundaryType.DESCRIPTION)}"
        )
        if self.builtin:
            lines.append(f"  {Boundary.open(BoundaryType.TYPE)}builtin{Boundary.close(BoundaryType.TYPE)}")
        lines.append(f"{Boundary.close(BoundaryType.SKILL)}")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Convert the skill to a markdown representation."""
        lines: list[str] = [Section.sub_heading(self.name, 2), "", self.instructions]
        if self.references:
            lines.append("")
            lines.append(Boundary.open(BoundaryType.SKILL_REFERENCES))
            for name in self.references.keys():
                lines.append(f"    {Boundary.open(BoundaryType.NAME)}{name}{Boundary.close(BoundaryType.NAME)}")
            lines.append(Boundary.close(BoundaryType.SKILL_REFERENCES))
        return MD.list_to_text(lines)
