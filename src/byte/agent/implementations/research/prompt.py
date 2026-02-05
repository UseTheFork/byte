from langchain_core.prompts import ChatPromptTemplate

from byte.code_operations import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

research_user_template = [
    Boundary.open(BoundaryType.USER_INPUT),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** consider the user input before proceeding (if not empty).",
    Boundary.close(BoundaryType.USER_INPUT),
    "{masked_messages}",
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- Search extensively for similar implementations and conventions in the codebase",
    "- Read relevant files to understand context and design decisions",
    "- Identify patterns, edge cases, and important considerations",
    "- Reference specific files and code examples in your findings",
    '- Explain "why" behind existing implementations when relevant',
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "Structure findings clearly:",
    "- Summary of discoveries",
    "- Specific file/code references",
    "- Relevant conventions and patterns",
    "- Important considerations or edge cases",
    "- Actionable recommendations",
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    "",
    Boundary.open(BoundaryType.GOAL),
    "Inform other agents with thorough research, not implement changes.",
    Boundary.close(BoundaryType.GOAL),
    "{project_information_and_context}",
    "{constraints_context}",
    "{project_hierarchy}",
    "{file_context_with_line_numbers}",
    "{operating_principles}",
]


research_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    "Act as an expert research assistant for codebase analysis.",
                    "You research and provide insights - you DO NOT make code changes.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)
