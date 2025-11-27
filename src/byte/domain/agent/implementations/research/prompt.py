from langchain_core.prompts import ChatPromptTemplate

from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary

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
                    "",
                    Boundary.open(BoundaryType.RULES),
                    "- Search extensively for similar implementations and conventions in the codebase",
                    "- Read relevant files to understand context and design decisions",
                    "- Identify patterns, edge cases, and important considerations",
                    "- Reference specific files and code examples in your findings",
                    '- Explain "why" behind existing implementations when relevant',
                    Boundary.close(BoundaryType.RULES),
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
                ]
            ),
        ),
        ("placeholder", "{project_inforamtion_and_context}"),
        ("placeholder", "{constraints_context}"),
        ("placeholder", "{masked_messages}"),
        ("user", "{processed_user_request}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{file_context_with_line_numbers}"),
        ("placeholder", "{errors}"),
    ]
)
