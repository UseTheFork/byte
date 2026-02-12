from langchain_core.prompts.chat import ChatPromptTemplate

from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

cleaner_user_template = [
    Boundary.open(BoundaryType.USER_INPUT),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** consider the user input before proceeding (if not empty).",
    Boundary.close(BoundaryType.USER_INPUT),
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- Remove: marketing fluff, legal boilerplate, repetitive examples, excessive formatting",
    "- Preserve: technical details, version numbers, API signatures, configuration values, caveats",
    "- Restructure: group related concepts, use clear hierarchy, prefer lists over prose",
    "- Maintain: original terminology, code snippets, important warnings or notes",
    "- Prioritize: actionable information over background context",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "- Return only the distilled content without meta-commentary.",
    "- Use markdown structure (headers, lists, code blocks) when it improves clarity.",
    "- Keep the output 30-70% of the original length while retaining 100% of the value.",
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    "{operating_principles}",
]

cleaner_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    "You are an expert content distiller who extracts signal from noise.",
                    "Transform verbose content into its essential form while preserving all critical information.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)
