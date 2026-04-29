from enum import StrEnum


class SectionType(StrEnum):
    """Type of boundary marker for content sections."""

    INTRODUCTION = "Introduction"

    ROLE = "Role"

    PROJECT_STATE = "Project State"
    REFERENCE_MATERIALS = "Reference Materials"
    PROJECT_ENVIRONMENT = "Project Environment"

    CONVERSATION_HISTORY = "Conversation History"
    USER_INPUT = "User Input"
    SKILLS = "Skills"
    AVALIABLE_SKILLS = "Avaliable Skills"
    TASK = "Task"

    OPERATING_CONSTRAINTS = "Operating Constraints"
    OPERATING_PRINCIPLES = "Operating Principles"

    COMMUNICATION_STYLE = "Communication Style"
    WORKFLOW = "Workflow"

    RESPONSE_FORMAT = "Response Format"
    RESUME_FORMAT = "Resuming The Conversation"

    EXAMPLES = "Examples"

    PLAN = "Plan"


class Section:
    """ """

    @staticmethod
    def start(
        section_type: SectionType,
    ) -> str:

        if not isinstance(section_type, SectionType):
            raise ValueError(f"section_type must be a SectionType enum, got {type(section_type).__name__}")

        anchor = section_type.value.lower().replace(" ", "-")

        return f"# Section: {section_type.value} [section-{anchor}]\n\n"

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
    ) -> str:

        if level not in (2, 3, 4):
            raise ValueError(f"level must be 2, 3, or 4, got {level}")

        return f"{'#' * level} {title}"

    @staticmethod
    def end() -> str:
        return "---\n\n"
