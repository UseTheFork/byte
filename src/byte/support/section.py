from enum import StrEnum


class SectionType(StrEnum):
    """Type of boundary marker for content sections."""

    INTRODUCTION = "Introduction"

    ROLE = "Role"

    PROJECT_FILES = "Workspace Files"
    REFERENCE_MATERIALS = "Reference Materials"
    PROJECT_ENVIRONMENT = "Workspace Environment"

    COMMIT_HISTORY = "Commit History"

    CONVERSATION_HISTORY = "Conversation History"

    CONSTITUTION = "Constitution"
    USER_INPUT = "User Input"
    SKILLS = "Skills"
    AVALIABLE_SKILLS = "Avaliable Skills"
    AVALIABLE_TOOLS = "Avaliable Tools"
    TASK = "Task"

    OPERATING_PRINCIPLES = "Operating Principles"

    COMMUNICATION_STYLE = "Communication Style"

    WORKFLOW = "Workflow"
    WORKFLOW_PHASES = "Workflow Phases"
    WORKFLOW_CONSTRAINTS = "Workflow Constraints"
    WORKFLOW_CURRENT_PHASE = "Current Workflow Phase"

    RESPONSE_FORMAT = "Response Format"
    RESUME_FORMAT = "Resuming The Conversation"

    EXAMPLES = "Examples"

    PLAN = "Plan"
    RULES = "Rules"


class Section:
    """ """

    @staticmethod
    def start(
        section_type: SectionType,
    ) -> str:

        if not isinstance(section_type, SectionType):
            raise ValueError(f"section_type must be a SectionType enum, got {type(section_type).__name__}")

        anchor = section_type.value.lower().replace(" ", "-")

        return f"# Section: {section_type.value} [section-{anchor}]\n"

    @staticmethod
    def ref(section_type: SectionType) -> str:
        anchor = section_type.value.lower().replace(" ", "-")
        return f"[{section_type.value}](#section-{anchor})"

    @staticmethod
    def important(
        message: str,
    ) -> str:
        return f"> **IMPORTANT**: {message}"

    @staticmethod
    def sub_heading(
        title: str,
        level: int,
        ref: bool = False,
    ) -> str:

        if level not in (2, 3, 4):
            raise ValueError(f"level must be 2, 3, or 4, got {level}")

        if ref:
            anchor = title.lower().replace(" ", "-")
            return f"{'#' * level} {title} [{title}](#{anchor})"

        return f"{'#' * level} {title}"

    @staticmethod
    def sub_heading_ref(title: str) -> str:
        anchor = title.lower().replace(" ", "-")
        return f"[{title}](#{anchor})"

    @staticmethod
    def end() -> str:
        return "---\n"
