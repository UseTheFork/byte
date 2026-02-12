import re
from typing import List

from byte.support.boundary import BoundaryType


class BoundaryExtractor:
    """Extract content from strings containing XML boundary blocks.

    This class parses strings with XML-style boundary tags and extracts
    content between opening and closing tags for a given BoundaryType.

    Usage:
        extractor = BoundaryExtractor()
        content = extractor.extract(text, BoundaryType.CONVENTION)
        all_contents = extractor.extract_all(text, BoundaryType.REFERENCE)
    """

    @staticmethod
    def extract(text: str, boundary_type: BoundaryType) -> str | None:
        """Extract the first occurrence of content within a given boundary type.

        Args:
            text: The string to search in
            boundary_type: The type of boundary to extract content from

        Returns:
            The content between the boundary tags, or None if not found

        Usage: `content = BoundaryExtractor.extract(text, BoundaryType.CONVENTION)`
        """
        if not isinstance(boundary_type, BoundaryType):
            raise ValueError(f"boundary_type must be a BoundaryType enum, got {type(boundary_type).__name__}")

        type_str = boundary_type.value

        # Pattern to match opening tag (with optional attributes), content, and closing tag
        pattern = rf"<{re.escape(type_str)}(?:\s+[^>]*)?>(.+?)</{re.escape(type_str)}>"

        match = re.search(pattern, text, re.DOTALL)

        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def extract_all(text: str, boundary_type: BoundaryType) -> List[str]:
        """Extract all occurrences of content within a given boundary type.

        Args:
            text: The string to search in
            boundary_type: The type of boundary to extract content from

        Returns:
            List of all content strings found between the boundary tags

        Usage: `contents = BoundaryExtractor.extract_all(text, BoundaryType.REFERENCE)`
        """
        if not isinstance(boundary_type, BoundaryType):
            raise ValueError(f"boundary_type must be a BoundaryType enum, got {type(boundary_type).__name__}")

        type_str = boundary_type.value

        # Pattern to match opening tag (with optional attributes), content, and closing tag
        pattern = rf"<{re.escape(type_str)}(?:\s+[^>]*)?>(.+?)</{re.escape(type_str)}>"

        matches = re.findall(pattern, text, re.DOTALL)

        return [match.strip() for match in matches]

    @staticmethod
    def extract_with_metadata(text: str, boundary_type: BoundaryType) -> List[dict]:
        """Extract content and metadata attributes from all occurrences of a boundary type.

        Args:
            text: The string to search in
            boundary_type: The type of boundary to extract content from

        Returns:
            List of dictionaries containing 'content' and 'attributes' keys

        Usage: `results = BoundaryExtractor.extract_with_metadata(text, BoundaryType.CONVENTION)`
        """
        if not isinstance(boundary_type, BoundaryType):
            raise ValueError(f"boundary_type must be a BoundaryType enum, got {type(boundary_type).__name__}")

        type_str = boundary_type.value

        # Pattern to capture opening tag with attributes, content, and closing tag
        pattern = rf"<{re.escape(type_str)}(\s+[^>]*)?>(.+?)</{re.escape(type_str)}>"

        results = []

        for match in re.finditer(pattern, text, re.DOTALL):
            attr_string = match.group(1) or ""
            content = match.group(2).strip()

            # Parse attributes from the opening tag
            attributes = {}
            if attr_string:
                # Pattern to match key="value" pairs
                attr_pattern = r'(\w+)="([^"]*)"'
                for attr_match in re.finditer(attr_pattern, attr_string):
                    key = attr_match.group(1)
                    value = attr_match.group(2)
                    attributes[key] = value

            results.append({"content": content, "attributes": attributes})

        return results
