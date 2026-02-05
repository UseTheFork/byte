from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class SkillProperties:
    """Properties parsed from a skill's SKILL.md frontmatter.

    Attributes:
        name: Skill name in kebab-case (required)
        description: What the skill does and when the model should use it (required)
        location: Path to the skill directory (required)
        metadata: Key-value pairs for client-specific properties (defaults to
            empty dict; omitted from to_dict() output when empty)
    """

    name: str
    description: str
    location: str
    metadata: dict[str, str] | None = Field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values.

        Usage: `skill_dict = properties.to_dict()` -> get dict representation
        """
        result = {"name": self.name, "description": self.description, "location": self.location}
        if self.metadata is not None and self.metadata:
            result["metadata"] = self.metadata
        return result
