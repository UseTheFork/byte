"""Service for parsing and validating SKILL.md files."""

import unicodedata
from pathlib import Path
from typing import Optional

from byte.parsing import ParsingService, SkillProperties, ValidationError

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024

# Allowed frontmatter fields for skills
ALLOWED_FIELDS = {
    "name",
    "description",
    "metadata",
}


class SkillParsingService(ParsingService):
    """Service for parsing and validating SKILL.md files.

    Provides methods to find, parse, validate, and generate prompts from
    skill directories containing SKILL.md files with YAML frontmatter.

    Usage: `service = app.make(SkillParsingService)`
    Usage: `properties = service.read_properties(skill_dir)`
    """

    def read_properties(self, file_path: Path | str) -> SkillProperties:
        """Read skill properties from Path md frontmatter.

        This function parses the frontmatter and returns properties.
        It does NOT perform full validation. Use validate() for that.

        Args:
            file_path: Path to the skill file (Path or str)

        Returns:
            SkillProperties with parsed metadata

        Raises:
            ParseError: If SKILL.md is missing or has invalid YAML
            ValidationError: If required fields (name, description) are missing

        Usage: `properties = service.read_properties(Path("/skills/my-skill.md"))`
        Usage: `properties = service.read_properties("/skills/my-skill.md")`
        """
        skill_path = Path(file_path)

        content = skill_path.read_text()
        metadata, _ = self.parse_frontmatter(content)

        if "name" not in metadata:
            raise ValidationError("Missing required field in frontmatter: name")
        if "description" not in metadata:
            raise ValidationError("Missing required field in frontmatter: description")

        name = metadata["name"]
        description = metadata["description"]

        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Field 'name' must be a non-empty string")
        if not isinstance(description, str) or not description.strip():
            raise ValidationError("Field 'description' must be a non-empty string")

        return SkillProperties(
            name=name.strip(),
            description=description.strip(),
            location=str(skill_path),
            metadata=metadata.get("metadata"),
        )

    def validate_name(self, name: str) -> list[str]:
        """Validate skill name format and directory match.

        Skill names support i18n characters (Unicode letters) plus hyphens.
        Names must be lowercase and cannot start/end with hyphens.

        Usage: `errors = service.validate_name("my-skill")`
        """
        errors = []

        if not name or not isinstance(name, str) or not name.strip():
            errors.append("Field 'name' must be a non-empty string")
            return errors

        name = unicodedata.normalize("NFKC", name.strip())

        if len(name) > MAX_SKILL_NAME_LENGTH:
            errors.append(f"Skill name '{name}' exceeds {MAX_SKILL_NAME_LENGTH} character limit ({len(name)} chars)")

        if name != name.lower():
            errors.append(f"Skill name '{name}' must be lowercase")

        if name.startswith("-") or name.endswith("-"):
            errors.append("Skill name cannot start or end with a hyphen")

        if "--" in name:
            errors.append("Skill name cannot contain consecutive hyphens")

        if not all(c.isalnum() or c == "-" for c in name):
            errors.append(
                f"Skill name '{name}' contains invalid characters. Only letters, digits, and hyphens are allowed."
            )

        return errors

    def validate_description(self, description: str) -> list[str]:
        """Validate description format.

        Usage: `errors = service.validate_description("My skill description")`
        """
        errors = []

        if not description or not isinstance(description, str) or not description.strip():
            errors.append("Field 'description' must be a non-empty string")
            return errors

        if len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"Description exceeds {MAX_DESCRIPTION_LENGTH} character limit ({len(description)} chars)")

        return errors

    def validate_metadata_fields(self, metadata: dict) -> list[str]:
        """Validate that only allowed fields are present.

        Usage: `errors = service.validate_metadata_fields(metadata)`
        """
        errors = []
        extra_fields = set(metadata.keys()) - ALLOWED_FIELDS
        if extra_fields:
            errors.append(
                f"Unexpected fields in frontmatter: {', '.join(sorted(extra_fields))}. "
                f"Only {sorted(ALLOWED_FIELDS)} are allowed."
            )
        return errors

    async def validate_metadata(self, metadata: dict, file_path: Optional[Path] = None) -> list[str]:
        """Validate parsed skill metadata.

        This is the core validation function that works on already-parsed metadata,
        avoiding duplicate file I/O when called from the parser.

        Args:
            metadata: Parsed YAML frontmatter dictionary
            skill_dir: Optional path to skill directory (for name-directory match check)

        Returns:
            List of validation error messages. Empty list means valid.

        Usage: `errors = await service.validate_metadata(metadata, skill_dir)`
        """
        errors = []

        errors.extend(self.validate_metadata_fields(metadata))

        if "name" not in metadata:
            errors.append("Missing required field in frontmatter: name")
        else:
            errors.extend(self.validate_name(metadata["name"]))

        if "description" not in metadata:
            errors.append("Missing required field in frontmatter: description")
        else:
            errors.extend(self.validate_description(metadata["description"]))

        return errors

    def format(
        self, name: str, description: str, content: str, metadata: Optional[dict[str, str]] = None, **kwargs
    ) -> str:
        """Format a complete skill string with YAML frontmatter.

        Args:
            name: Skill name (kebab-case, max 64 chars)
            description: Skill description (max 1024 chars)
            content: Markdown body content
            metadata: Optional key-value metadata pairs

        Returns:
            Fully formatted skill string with frontmatter and content

        Usage: `skill_str = service.format("my-skill", "Does something", "# Content")`
        Usage: `skill_str = service.format("my-skill", "Does something", "# Content", {"key": "value"})`
        """
        lines = ["---", f"name: {name}", f"description: {description}"]

        if metadata:
            lines.append("metadata:")
            for key, value in metadata.items():
                lines.append(f"  {key}: {value}")

        lines.append("---")
        lines.append(content)

        return "\n".join(lines)

    def parse(self, content: str) -> SkillProperties:
        """Parse a complete skill string with YAML frontmatter into SkillProperties.

        Args:
            content: The complete file content including frontmatter and body

        Returns:
            SkillProperties object with parsed metadata and content

        Raises:
            ParseError: If the content has invalid YAML or missing frontmatter
            ValidationError: If required fields are missing or invalid

        Usage: `properties = service.parse(file_content)`
        """
        metadata, body = self.parse_frontmatter(content)

        if "name" not in metadata:
            raise ValidationError("Missing required field in frontmatter: name")
        if "description" not in metadata:
            raise ValidationError("Missing required field in frontmatter: description")

        name = metadata["name"]
        description = metadata["description"]

        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Field 'name' must be a non-empty string")
        if not isinstance(description, str) or not description.strip():
            raise ValidationError("Field 'description' must be a non-empty string")

        return SkillProperties(
            name=name.strip(),
            description=description.strip(),
            location="",  # Location is not available from parsed content
            content=body.strip(),
            metadata=metadata.get("metadata"),
        )
