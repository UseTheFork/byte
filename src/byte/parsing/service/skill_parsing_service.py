"""Service for parsing and validating SKILL.md files."""

import unicodedata
from pathlib import Path
from typing import Optional

import strictyaml

from byte.parsing.exceptions import ParseError, ValidationError
from byte.parsing.schemas import SkillProperties
from byte.support import Service

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024

# Allowed frontmatter fields
ALLOWED_FIELDS = {
    "name",
    "description",
    "metadata",
}


class SkillParsingService(Service):
    """Service for parsing and validating SKILL.md files.

    Provides methods to find, parse, validate, and generate prompts from
    skill directories containing SKILL.md files with YAML frontmatter.

    Usage: `service = app.make(SkillParsingService)`
    Usage: `properties = await service.read_properties(skill_dir)`
    """

    def parse_frontmatter(self, content: str) -> tuple[dict, str]:
        """Parse YAML frontmatter from SKILL.md content.

        Args:
            content: Raw content of SKILL.md file

        Returns:
            Tuple of (metadata dict, markdown body)

        Raises:
            ParseError: If frontmatter is missing or invalid

        Usage: `metadata, body = service.parse_frontmatter(content)`
        """
        if not content.startswith("---"):
            raise ParseError("must start with YAML frontmatter (---)")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ParseError("frontmatter not properly closed with ---")

        frontmatter_str = parts[1]
        body = parts[2].strip()

        try:
            parsed = strictyaml.load(frontmatter_str)
            metadata = parsed.data
        except strictyaml.YAMLError as e:
            raise ParseError(f"Invalid YAML in frontmatter: {e}")

        if not isinstance(metadata, dict):
            raise ParseError("frontmatter must be a YAML mapping")

        if "metadata" in metadata and isinstance(metadata["metadata"], dict):
            metadata["metadata"] = {str(k): str(v) for k, v in metadata["metadata"].items()}

        return metadata, body

    def read_properties(self, skill_path: Path) -> SkillProperties:
        """Read skill properties from Path md frontmatter.

        This function parses the frontmatter and returns properties.
        It does NOT perform full validation. Use validate() for that.

        Args:
            skill_dir: Path to the skill directory

        Returns:
            SkillProperties with parsed metadata

        Raises:
            ParseError: If SKILL.md is missing or has invalid YAML
            ValidationError: If required fields (name, description) are missing

        Usage: `properties = await service.read_properties(Path("/skills/my-skill.md"))`
        """
        skill_path = Path(skill_path)

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

        Usage: `errors = service._validate_name("my-skill", skill_dir)`
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

        Usage: `errors = service._validate_metadata_fields(metadata)`
        """
        errors = []
        extra_fields = set(metadata.keys()) - ALLOWED_FIELDS
        if extra_fields:
            errors.append(
                f"Unexpected fields in frontmatter: {', '.join(sorted(extra_fields))}. "
                f"Only {sorted(ALLOWED_FIELDS)} are allowed."
            )
        return errors

    async def validate_metadata(self, metadata: dict, skill_dir: Optional[Path] = None) -> list[str]:
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

    def read_skill_content(self, skill_path: str | Path) -> str:
        """Read and validate a skill file, returning only the markdown body.

        This method validates the skill file by parsing its frontmatter via
        read_properties(), then returns the markdown content without the frontmatter.

        Args:
            skill_path: Path to the skill markdown file (string or Path object)

        Returns:
            The markdown body content (without YAML frontmatter)

        Raises:
            ParseError: If the file has invalid YAML or missing frontmatter
            ValidationError: If required fields are missing or invalid

        Usage: `content = service.read_skill_content("path/to/skill.md")`
        Usage: `content = service.read_skill_content(Path("path/to/skill.md"))`
        """
        skill_path = Path(skill_path)

        # Validate the file by reading properties (raises exceptions if invalid)
        self.read_properties(skill_path)

        # Read the file content and extract just the body
        content = skill_path.read_text()
        _, body = self.parse_frontmatter(content)

        return body

    def format_skill(self, name: str, description: str, content: str, metadata: Optional[dict[str, str]] = None) -> str:
        """Format a complete skill string with YAML frontmatter.

        Args:
            name: Skill name (kebab-case, max 64 chars)
            description: Skill description (max 1024 chars)
            content: Markdown body content
            metadata: Optional key-value metadata pairs

        Returns:
            Fully formatted skill string with frontmatter and content

        Usage: `skill_str = service.format_skill("my-skill", "Does something", "# Content")`
        Usage: `skill_str = service.format_skill("my-skill", "Does something", "# Content", {"key": "value"})`
        """
        lines = ["---", f"name: {name}", f"description: {description}"]

        if metadata:
            lines.append("metadata:")
            for key, value in metadata.items():
                lines.append(f"  {key}: {value}")

        lines.append("---")
        lines.append(content)

        return "\n".join(lines)
