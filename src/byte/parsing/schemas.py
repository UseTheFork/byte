from pydantic import Field
from pydantic.dataclasses import dataclass

from byte.support.string import Str


@dataclass
class Properties:
    """Base properties class for parsed file frontmatter.

    Attributes:
        name: Resource name (required)
        description: What the resource does (required)
        location: Path to the resource file (required)
        content: Optional markdown body content (without frontmatter)
        metadata: Key-value pairs for client-specific properties (defaults to
            empty dict; omitted from to_dict() output when empty)
    """

    name: str
    description: str
    location: str | None = None
    content: str | None = None
    metadata: dict[str, str] | None = Field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values.

        Usage: `properties.to_dict()` -> get dict representation
        """
        result = {"name": self.name, "description": self.description, "location": self.location}
        if self.metadata is not None and self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class SkillProperties(Properties):
    """Properties parsed from a skill's SKILL.md frontmatter.

    Attributes:
        name: Skill name in kebab-case (required)
        description: What the skill does and when the model should use it (required)
        location: Path to the skill directory (required)
        metadata: Key-value pairs for client-specific properties (defaults to
            empty dict; omitted from to_dict() output when empty)
    """

    pass


@dataclass
class ConventionProperties(Properties):
    """Properties parsed from a convention's .md frontmatter.

    Attributes:
        name: Convention name (required)
        description: What the convention provides (required)
        location: Path to the convention file (required)
        references: List of paths to reference documentation files (optional)
        metadata: Key-value pairs for client-specific properties (defaults to
            empty dict; omitted from to_dict() output when empty)
    """

    def generate_convention_frontmatter(self) -> str:
        """Generate YAML frontmatter for a convention file using instance properties.

        Returns:
            Formatted YAML frontmatter string with opening and closing delimiters

        Usage: `frontmatter = convention_props.generate_convention_frontmatter()`
        """
        lines = ["---", f"name: {self.name}", f"description: {self.description}"]

        if self.metadata:
            lines.append("metadata:")
            for key, value in self.metadata.items():
                lines.append(f"  {key}: {value}")

        lines.append("---")

        return "\n".join(lines)

    def filename(self) -> str:
        """Generate a filename from the convention name using underscores as separators.

        Returns:
            Filename string ending in .md with underscores as separators

        Usage: `filename = convention_props.generate_filename()`
        """
        return f"{Str.slugify(self.name, '_')}.md"
