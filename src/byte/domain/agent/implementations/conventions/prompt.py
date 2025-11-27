from langchain_core.prompts.chat import ChatPromptTemplate

from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary

conventions_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    "Act as an expert technical writer specializing in creating concise, actionable coding conventions.",
                    Boundary.close(BoundaryType.ROLE),
                    "",
                    Boundary.open(BoundaryType.TASK),
                    "You will be provided with code files and a focus area for the convention.",
                    "Your task is to analyze the code and create a convention document that captures:",
                    "- Key patterns and practices used in the codebase",
                    "- Naming conventions and code structure",
                    "- Important design decisions and rationale",
                    "- Specific examples from the provided code",
                    Boundary.close(BoundaryType.TASK),
                    "",
                    Boundary.open(BoundaryType.RULES),
                    "- Keep conventions SHORT and focused - these are always loaded by AI agents",
                    "- Use concrete examples from the provided code",
                    '- Focus only on the requested aspect (e.g., "Python style", "API design", "error handling")',
                    "- Use bullet points and clear headings for scannability",
                    '- Include "why" behind conventions when it\'s not obvious',
                    "- Avoid generic advice - be specific to this codebase",
                    "- Format code examples with proper syntax highlighting",
                    "- Never use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
                    Boundary.close(BoundaryType.RULES),
                    "",
                    Boundary.open(BoundaryType.RESPONSE_FORMAT),
                    "Structure your convention document as:",
                    "1. Brief title describing the convention focus",
                    "2. Key principles (2-4 bullet points)",
                    "4. Common patterns to follow",
                    "5. Things to avoid (if applicable)",
                    "",
                    "Keep the entire document under 50 lines.",
                    Boundary.close(BoundaryType.RESPONSE_FORMAT),
                    "",
                    Boundary.open(BoundaryType.GOAL),
                    "Create a convention file that AI agents can quickly reference to maintain consistency",
                    "with the existing codebase patterns and practices.",
                    Boundary.close(BoundaryType.GOAL),
                ]
            ),
        ),
        ("placeholder", "{project_inforamtion_and_context}"),
        ("placeholder", "{project_hierarchy}"),
        ("placeholder", "{file_context_with_line_numbers}"),
        ("user", "{processed_user_request}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)
