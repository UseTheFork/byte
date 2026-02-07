"""Service for parsing and validating CONVENTION.md files."""

from pathlib import Path
from typing import Optional

from byte.parsing import ConventionProperties, ParsingService, ValidationError

MAX_CONVENTION_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024

# Allowed frontmatter fields for convention
ALLOWED_FIELDS = {
    "name",
    "description",
}


class ConventionParsingService(ParsingService):
    """Service for parsing and validating CONVENTION.md files.

    Provides methods to parse, validate, and generate convention files
    containing CONVENTION.md files with YAML frontmatter.

    Usage: `service = app.make(ConventionParsingService)`
    Usage: `properties = service.read_properties(convention_path)`
    """

    def read_properties(self, file_path: Path | str) -> ConventionProperties:
        """Read skill properties from Path md frontmatter.

        This function parses the frontmatter and returns properties.
        It does NOT perform full validation. Use validate() for that.

        Args:
            file_path: Path to the skill file (Path or str)

        Returns:
            ConventionProperties with parsed metadata

        Raises:
            ParseError: If SKILL.md is missing or has invalid YAML
            ValidationError: If required fields (name, description) are missing

        Usage: `properties = service.read_properties(Path("/skills/my-skill.md"))`
        Usage: `properties = service.read_properties("/skills/my-skill.md")`
        """
        convention_path = Path(file_path)

        content = convention_path.read_text()
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

        return ConventionProperties(
            name=name.strip(),
            description=description.strip(),
            metadata=metadata.get("metadata"),
        )

    def validate_name(self, name: str) -> list[str]:
        """Validate convention name format.

        Usage: `errors = service.validate_name("my-convention")`
        """
        errors = []

        if not name or not isinstance(name, str) or not name.strip():
            errors.append("Field 'name' must be a non-empty string")
            return errors

        if len(name) > MAX_CONVENTION_NAME_LENGTH:
            errors.append(
                f"Convention name '{name}' exceeds {MAX_CONVENTION_NAME_LENGTH} character limit ({len(name)} chars)"
            )

        return errors

    def validate_description(self, description: str) -> list[str]:
        """Validate description format.

        Usage: `errors = service.validate_description("My convention description")`
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
        """Validate parsed convention metadata.

        This is the core validation function that works on already-parsed metadata,
        avoiding duplicate file I/O when called from the parser.

        Args:
            metadata: Parsed YAML frontmatter dictionary
            file_path: Optional path to convention file (for additional validation checks)

        Returns:
            List of validation error messages. Empty list means valid.

        Usage: `errors = await service.validate_metadata(metadata, file_path)`
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
        """Format a complete convention string with YAML frontmatter.

        Args:
            name: Convention name (max 64 chars)
            description: Convention description (max 1024 chars)
            content: Markdown body content
            metadata: Optional key-value metadata pairs

        Returns:
            Fully formatted convention string with frontmatter and content

        Usage: `convention_str = service.format("my-convention", "Does something", "# Content")`
        Usage: `convention_str = service.format("my-convention", "Does something", "# Content", {"key": "value"})`
        """
        lines = ["---", f"name: {name}", f"description: {description}"]

        if metadata:
            lines.append("metadata:")
            for key, value in metadata.items():
                lines.append(f"  {key}: {value}")

        lines.append("---")
        lines.append(content)

        return "\n".join(lines)

    def parse(self, content: str) -> ConventionProperties:
        """Parse a complete skill string with YAML frontmatter into ConventionProperties.

        Args:
            content: The complete file content including frontmatter and body

        Returns:
            ConventionProperties object with parsed metadata and content

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

        return ConventionProperties(
            name=name.strip(),
            description=description.strip(),
            content=body.strip(),
            metadata=metadata.get("metadata"),
        )
