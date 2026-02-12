"""Base service for parsing and validating files with YAML frontmatter."""

from abc import abstractmethod
from pathlib import Path
from typing import Optional

import strictyaml

from byte.parsing.exceptions import ParseError
from byte.parsing.schemas import Properties
from byte.support import Service


class ParsingService(Service):
    """Base service for parsing and validating files with YAML frontmatter.

    This is an abstract base class that provides core parsing functionality
    for files with YAML frontmatter. Concrete implementations should extend
    this class and implement validation methods for their specific file types.

    Usage: `class MyParsingService(ParsingService): ...`
    """

    def parse_frontmatter(self, content: str) -> tuple[dict, str]:
        """Parse YAML frontmatter from file content.

        Args:
            content: Raw content of file

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

    @abstractmethod
    def read_properties(self, file_path: Path | str) -> Properties:
        """Read properties from file frontmatter.

        This method should parse the frontmatter and return a properties object.
        It does NOT perform full validation. Use validate() for that.

        Args:
            file_path_or_str: Path to the file

        Returns:
            Properties object specific to the file type

        Raises:
            ParseError: If file is missing or has invalid YAML
            ValidationError: If required fields are missing

        Usage: `properties = service.read_properties(Path("/path/to/file.md"))`
        """
        pass

    @abstractmethod
    def validate_metadata_fields(self, metadata: dict) -> list[str]:
        """Validate that only allowed fields are present.

        Args:
            metadata: Parsed YAML frontmatter dictionary

        Returns:
            List of validation error messages. Empty list means valid.

        Usage: `errors = service.validate_metadata_fields(metadata)`
        """
        pass

    @abstractmethod
    async def validate_metadata(self, metadata: dict, file_path: Optional[Path] = None) -> list[str]:
        """Validate parsed metadata.

        This is the core validation function that works on already-parsed metadata,
        avoiding duplicate file I/O when called from the parser.

        Args:
            metadata: Parsed YAML frontmatter dictionary
            file_path: Optional path to file (for additional validation checks)

        Returns:
            List of validation error messages. Empty list means valid.

        Usage: `errors = await service.validate_metadata(metadata, file_path)`
        """
        pass

    def read_content(self, file_path: str | Path) -> str:
        """Read and validate a file, returning only the markdown body.

        This method validates the file by parsing its frontmatter via
        read_properties(), then returns the markdown content without the frontmatter.

        Args:
            file_path: Path to the markdown file (string or Path object)

        Returns:
            The markdown body content (without YAML frontmatter)

        Raises:
            ParseError: If the file has invalid YAML or missing frontmatter
            ValidationError: If required fields are missing or invalid

        Usage: `content = service.read_content("path/to/file.md")`
        Usage: `content = service.read_content(Path("path/to/file.md"))`
        """
        file_path = Path(file_path)

        # Validate the file by reading properties (raises exceptions if invalid)
        self.read_properties(file_path)

        # Read the file content and extract just the body
        content = file_path.read_text()
        _, body = self.parse_frontmatter(content)

        return body

    @abstractmethod
    def format(self, **kwargs) -> str:
        """Format a complete file string with YAML frontmatter.

        Args:
            **kwargs: All fields specific to the file type (including content)

        Returns:
            Fully formatted file string with frontmatter and content

        Usage: `file_str = service.format(content="# Content", name="my-file", description="Does something")`
        """
        pass

    @abstractmethod
    def parse(self, content: str) -> Properties:
        """Parse a complete file string with YAML frontmatter into Properties.

        Args:
            content: The complete file content including frontmatter and body

        Returns:
            Properties object with parsed metadata and content

        Raises:
            ParseError: If the content has invalid YAML or missing frontmatter
            ValidationError: If required fields are missing or invalid

        Usage: `properties = service.parse(file_content)`
        """
        pass
