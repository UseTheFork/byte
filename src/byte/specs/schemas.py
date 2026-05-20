from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Spec:
    """Represents a parsed spec file (``YYYY-MM-DD-<topic>-spec.md``).

    Attributes:
        name: Unique spec name (from frontmatter).
        description: Short description of the spec (from frontmatter).
        instructions: Body content of the spec file (after frontmatter).
        path: Directory containing the spec file.
        spec_file_path: Absolute path to the spec file.
        version: Optional version string (from frontmatter).
        tags: Optional list of tags (from frontmatter).
    """

    name: str
    description: str
    instructions: str
    path: Path
    spec_file_path: Path
    version: Optional[str] = None
    tags: Optional[list[str]] = None
