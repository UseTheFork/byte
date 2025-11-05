from typing import Literal

from byte.domain.edit_format.schemas import BoundaryType


def boundary(
    boundary_type: BoundaryType | str,
    opening: bool = True,
    meta: dict[str, str] | None = None,
    format_style: Literal["xml", "markdown"] = "xml",
) -> str:
    """Format opening or closing tags in XML or Markdown style.

    Usage:
    `boundary(BoundaryType.CONVENTION, True, {"title": "Style Guide"}, "xml")`
    -> '<convention: title="Style Guide" >'

    `boundary(BoundaryType.CONVENTION, False, None, "xml")`
    -> '</convention>'

    `boundary(BoundaryType.CONVENTION, True, {"title": "Style Guide"}, "markdown")`
    -> '## Convention: Style Guide'
    """
    # Convert enum to string if needed
    type_str = boundary_type.value if isinstance(boundary_type, BoundaryType) else boundary_type

    if format_style == "xml":
        if opening:
            # Build meta attributes string
            meta_str = ""
            if meta:
                meta_parts = [f'{key}="{value}"' for key, value in meta.items()]
                meta_str = " ".join(meta_parts) + " "

            return f"<{type_str}{meta_str}>"
        else:
            return f"</{type_str}>"

    elif format_style == "markdown":
        if opening:
            # Build meta title string
            title_str = ""
            if meta and "title" in meta:
                title_str = f": {meta['title']}"

            return f"## {type_str.title()}{title_str}"
        else:
            # Markdown doesn't have closing tags
            return ""

    else:
        raise ValueError(f"Unsupported format_style: {format_style}")
