from enum import Enum


class BoundaryType(str, Enum):
    """Type of boundary marker for content sections."""

    ROLE = "role"
    TASK = "task"
    USER_INPUT = "user_input"

    CORE_MANDATES = "core_mandates"

    GOAL = "goal"
    RESPONSE_FORMAT = "response_format"

    RULES = "rules"

    ERROR = "error"

    NAME = "name"
    DESCRIPTION = "description"
    LOCATION = "location"

    AVAILABLE_CONVENTIONS = "available_conventions"
    CONVENTION = "convention"

    REFERENCE = "reference"

    SESSION_CONTEXT = "session_context"
    SHELL_COMMAND = "shell_command"

    FILE = "file"

    EDIT_BLOCK = "operation_block"
    SEARCH = "search"
    REPLACE = "replace"
    EXAMPLE = "example"
    REINFORCEMENT = "reinforcement"
    PROJECT_HIERARCHY = "project_hierarchy"
    CONSTRAINTS = "constraints"
    PLAN = "agent_plan"

    # Operating Constraints
    GUIDELINES = "guidelines"
    OPERATING_CONSTRAINTS = "operating_constraints"
    OPERATING_PRINCIPLES = "operating_principles"

    CRITICAL_REQUIREMENTS = "response_requirements"
    RECOVERY_STEPS = "recovery_steps"

    RESPONSE_TEMPLATE = "response_template"

    CONTEXT = "context"

    GIT_CONTEXT = "git_context"

    # Specific to command execution
    STDOUT = "stdout"
    STDERR = "stderr"

    SYSTEM_CONTEXT = "system_context"

    NOTE = "note"

    HEADING = "heading"

    CONVERSATION_HISTORY = "conversation_history"
    AGENT_MESSAGE = "agent_message"
    TOOL_CALL = "tool_call"
    USER_MESSAGE = "user_message"

    def __str__(self):
        return self.value


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
