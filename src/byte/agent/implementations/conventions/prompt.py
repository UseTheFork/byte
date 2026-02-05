from langchain_core.prompts.chat import ChatPromptTemplate

from byte.prompt_format import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

conventions_user_template = [
    Boundary.open(BoundaryType.USER_INPUT),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** consider the user input before proceeding (if not empty).",
    Boundary.close(BoundaryType.USER_INPUT),
    "",
    Boundary.open(BoundaryType.TASK),
    "You will be provided with code files and a focus area for the convention.",
    "Your task is to analyze the code and create a convention document that captures:",
    "- Key patterns and practices used in the codebase",
    "- Naming conventions and code structure",
    "- Important design decisions and rationale",
    "- Specific examples from the provided code",
    "",
    "Conventions are single Markdown files (not multi-file packages). They do not include scripts, assets, or separate reference files.",
    Boundary.close(BoundaryType.TASK),
    "",
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- **Concise is key**: The context window is a public good. Conventions are always loaded by AI agents, so every token counts.",
    "- **Default assumption: Byte is already very smart.** Only add context Byte doesn't already have.",
    "- Challenge each piece of information: 'Does Byte really need this explanation?' and 'Does this paragraph justify its token cost?'",
    "- Prefer concise examples over verbose explanations",
    "- Use concrete examples from the provided code",
    '- Focus only on the requested aspect (e.g., "Python style", "API design", "error handling")',
    "- Use bullet points and clear headings for scannability",
    '- Include "why" behind conventions when it\'s not obvious',
    "- Avoid generic advice - be specific to this codebase",
    "- Format code examples with proper syntax highlighting",
    "- Never use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    Boundary.open(BoundaryType.CRITICAL_REQUIREMENTS),
    "You MUST follow the exact template structure provided below.",
    "This template is REQUIRED and must be followed precisely.",
    "Do not deviate from this structure.",
    Boundary.close(BoundaryType.CRITICAL_REQUIREMENTS),
    Boundary.open(BoundaryType.RESPONSE_TEMPLATE),
    Boundary.important("You MUST follow the below template to be successful."),
    "```text",
    "---",
    "name: template-convention",
    "description: Replace with description of the convention and when Byte should use it.",
    "---",
    "",
    "# Insert instructions below",
    "```",
    Boundary.close(BoundaryType.RESPONSE_TEMPLATE),
    Boundary.open(BoundaryType.GOAL),
    "Create a convention file that AI agents can quickly reference to maintain consistency",
    "with the existing codebase patterns and practices.",
    Boundary.close(BoundaryType.GOAL),
    "{project_information_and_context}",
    "{project_hierarchy}",
    "{file_context_with_line_numbers}",
    "{operating_principles}",
]

conventions_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    "You are Byte, a human-in-the-loop AI coding agent.",
                    "Act as an expert technical writer specializing in creating concise, actionable coding conventions.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)
