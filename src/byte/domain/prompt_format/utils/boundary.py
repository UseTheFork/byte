from typing import Literal

from byte.domain.prompt_format.schemas import BoundaryType


class Boundary:
    """Format opening and closing tags in XML or Markdown style.

    Usage:
    `Boundary.open(BoundaryType.CONVENTION, {"title": "Style Guide"}, "xml")`
    -> '<convention title="Style Guide">'

    `Boundary.close(BoundaryType.CONVENTION, "xml")`
    -> '</convention>'

    `Boundary.open(BoundaryType.CONVENTION, {"title": "Style Guide"}, "markdown")`
    -> '## Convention: Style Guide'
    """

    @staticmethod
    def open(
        boundary_type: BoundaryType,
        meta: dict[str, str] | None = None,
        format_style: Literal["xml", "markdown"] = "xml",
    ) -> str:
        """Format opening tags in XML or Markdown style.

        Args:
                boundary_type: Type of boundary marker
                meta: Optional metadata dictionary
                format_style: Output format style ('xml' or 'markdown')

        Returns:
                Formatted opening tag string

        Usage: `Boundary.open(BoundaryType.CONVENTION, {"title": "Guide"}, "xml")`
        """
        if not isinstance(boundary_type, BoundaryType):
            raise ValueError(f"boundary_type must be a BoundaryType enum, got {type(boundary_type).__name__}")

        if format_style not in ("xml", "markdown"):
            raise ValueError(f"format_style must be 'xml' or 'markdown', got {format_style!r}")

        type_str = boundary_type.value

        if format_style == "xml":
            # Build meta attributes string
            meta_str = ""
            if meta:
                meta_parts = [f'{key}="{value}"' for key, value in meta.items()]
                meta_str = " " + " ".join(meta_parts)

            return f"<{type_str}{meta_str}>"

        elif format_style == "markdown":
            # Build meta title string
            title_str = ""
            if meta and "title" in meta:
                title_str = f": {meta['title']}"

            return f"## {type_str.title()}{title_str}"

        else:
            raise ValueError(f"Unsupported format_style: {format_style}")

    @staticmethod
    def close(
        boundary_type: BoundaryType,
        format_style: Literal["xml", "markdown"] = "xml",
    ) -> str:
        """Format closing tags in XML or Markdown style.

        Args:
                boundary_type: Type of boundary marker
                format_style: Output format style ('xml' or 'markdown')

        Returns:
                Formatted closing tag string (empty for markdown)

        Usage: `Boundary.close(BoundaryType.CONVENTION, "xml")`
        """
        if not isinstance(boundary_type, BoundaryType):
            raise ValueError(f"boundary_type must be a BoundaryType enum, got {type(boundary_type).__name__}")

        if format_style not in ("xml", "markdown"):
            raise ValueError(f"format_style must be 'xml' or 'markdown', got {format_style!r}")

        type_str = boundary_type.value

        if format_style == "xml":
            return f"</{type_str}>"
        elif format_style == "markdown":
            # Markdown doesn't have closing tags
            return ""
        else:
            raise ValueError(f"Unsupported format_style: {format_style}")

    @staticmethod
    def notice(
        content: str,
        format_style: Literal["xml", "markdown"] = "xml",
    ) -> str:
        """Wrap content in notice tags to emphasize important information.

        Args:
                content: The content to wrap
                format_style: Output format style ('xml' or 'markdown')

        Returns:
                Formatted notice string with content

        Usage: `Boundary.notice("Any edits to these files will be rejected", "xml")`
        """
        if format_style not in ("xml", "markdown"):
            raise ValueError(f"format_style must be 'xml' or 'markdown', got {format_style!r}")

        if format_style == "xml":
            return f"<notice>**{content}**</notice>"
        elif format_style == "markdown":
            return f"**{content}**"
        else:
            raise ValueError(f"Unsupported format_style: {format_style}")
