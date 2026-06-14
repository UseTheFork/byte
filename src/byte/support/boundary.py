from enum import StrEnum


class BoundaryType(StrEnum):
    """Type of boundary marker for content sections."""

    CORE_MANDATES = "core_mandates"

    RULES = "rules"

    ERROR = "error"

    # genaric
    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"
    LOCATION = "location"
    TYPE = "type"

    # conventions
    AVAILABLE_CONVENTIONS = "available_conventions"
    CONVENTION = "convention"
    # / conventions

    SESSION_CONTEXT = "session_context"
    SHELL_COMMAND = "shell_command"

    FILE = "file"

    EXAMPLE = "example"

    PROJECT_HIERARCHY = "project_hierarchy"
    CONSTRAINTS = "constraints"

    AVAILABLE_TOOLS = "available_tools"
    TOOL = "tool"

    # Skills
    AVAILABLE_SKILLS = "available_skills"
    SKILL_REFERENCES = "skill_references"
    SKILL = "skill"

    # Operating Constraints

    CONTEXT = "context"

    # Specific to command execution
    STDOUT = "stdout"
    STDERR = "stderr"

    AGENT_MESSAGE = "agent_message"
    USER_MESSAGE = "user_message"
    TOOL_CALL = "tool_call"


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

        type_str = boundary_type.value

        # Build meta attributes string
        meta_str = ""
        if meta:
            meta_parts = [f'{key}="{value}"' for key, value in meta.items()]
            meta_str = " " + " ".join(meta_parts)

        return f"<{type_str}{meta_str}>"

    @staticmethod
    def close(boundary_type: BoundaryType) -> str:
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

        type_str = boundary_type.value

        return f"</{type_str}>"

    @staticmethod
    def notice(
        content: str,
    ) -> str:
        """Wrap content in notice tags to emphasize important information.

        Args:
                content: The content to wrap

        Returns:
                Formatted notice string with content

        Usage: `Boundary.notice("Any edits to these files will be rejected")`
        """
        return f"<notice>{content}<notice>"

    @staticmethod
    def critical(
        content: str,
    ) -> str:
        """Wrap content in critical tags to emphasize critical information.

        Args:
                content: The content to wrap

        Returns:
                Formatted critical string with content

        Usage: `Boundary.critical("This action cannot be undone")`
        """
        return f"<critical>You **MUST** consider the following before proceeding:\n\n**{content}**</critical>"

    @staticmethod
    def important(
        content: str,
    ) -> str:
        """Wrap content in important tags to emphasize important information.

        Args:
                content: The content to wrap

        Returns:
                Formatted important string with content

        Usage: `Boundary.important("Please review carefully")`
        """
        return f"<important>**{content}**</important>"

    @staticmethod
    def warning(
        content: str,
    ) -> str:
        """Wrap content in warning tags to emphasize warning information.

        Args:
                content: The content to wrap

        Returns:
                Formatted warning string with content

        Usage: `Boundary.warning("This may cause unexpected behavior")`
        """
        return f"<warning>{content}</warning>"

    @staticmethod
    def comment(content: str) -> str:
        return f"<comment>{content}</comment>"
