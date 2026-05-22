from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from byte.support import MD
from byte.support.utils import list_to_multiline_text


@dataclass
class SpecTaskFiles:
    """Represents files associated with a spec phase.

    Attributes:
        reference: Files that should be referenced but not modified.
        create: Files that need to be created.
        edit: Files that need to be edited.
    """

    reference: list[str] = field(default_factory=list)
    create: list[str] = field(default_factory=list)
    edit: list[str] = field(default_factory=list)


@dataclass
class SpecTask:
    """Represents a single execution phase attached to a spec.

    Phases are persisted as individual markdown files with YAML frontmatter
    in the ``phases/`` subdirectory alongside the ``SPEC.md`` file.

    Attributes:
        id: Unique phase identifier (e.g. ``"phase-1"``).
        order: Numeric order for loading and sequencing phases.
        status: Current execution status.
        content: Description of what this phase should accomplish.
        notes: Ordered list of additional notes or observations for the phase.
        files: Files associated with the phase (reference, create, edit).
    """

    id: str
    order: int = 0
    status: Literal["pending", "in_progress", "blocked", "completed"] = "pending"
    content: str = ""
    notes: list[str] = field(default_factory=list)
    files: SpecTaskFiles = field(default_factory=SpecTaskFiles)

    def to_md(self) -> str:
        lines = [
            MD.bullet(f"ID: {self.id}"),
            MD.bullet(f"Order: {self.order}"),
            MD.bullet(f"Status: {self.status}"),
            self.content,
        ]

        if self.notes:
            lines.append("")
            lines.append("**Notes:**")
            for note in self.notes:
                lines.append(MD.bullet(note))

        if self.files.reference or self.files.create or self.files.edit:
            lines.append("")
            lines.append("**Files:**")
            if self.files.reference:
                lines.append(MD.bullet("Reference:"))
                for file in self.files.reference:
                    lines.append(MD.bullet(file, level=2))
            if self.files.create:
                lines.append(MD.bullet("Create:"))
                for file in self.files.create:
                    lines.append(MD.bullet(file, level=2))
            if self.files.edit:
                lines.append(MD.bullet("Edit:"))
                for file in self.files.edit:
                    lines.append(MD.bullet(file, level=2))

        return list_to_multiline_text(lines)


@dataclass
class Spec:
    """Represents a parsed spec file (``<topic>/SPEC.md``).

    Attributes:
        name: Unique spec name (from frontmatter).
        description: Short description of the spec (from frontmatter).
        instructions: Body content of the spec file (after frontmatter).
        path: Directory containing the spec file.
        spec_file_path: Absolute path to the spec file.
        reference_files: Optional list of reference files (from frontmatter).
    """

    id: str
    name: str
    description: str
    instructions: str
    path: Path
    spec_file_path: Path
    reference_files: list[str] = field(default_factory=list)

    def to_md(self) -> str:
        return list_to_multiline_text(
            [
                MD.bullet(f"ID: {self.id}"),
                MD.bullet(f"Name: {self.name}"),
                "",
                self.instructions,
            ]
        )
