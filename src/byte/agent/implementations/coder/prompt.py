from langchain_core.prompts import ChatPromptTemplate

from byte.prompt_format import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

coder_user_template = [
    Boundary.open(BoundaryType.USER_INPUT),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** consider the user input before proceeding (if not empty).",
    Boundary.close(BoundaryType.USER_INPUT),
    "",
    "{masked_messages}",
    "",
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- Always use best practices when coding",
    "- Respect and use existing conventions, libraries, etc that are already present in the code base",
    "- Take requests for changes to the supplied code",
    "- If the request is ambiguous, ask clarifying questions before proceeding",
    "- Keep changes simple don't build more then what is asked for",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "{edit_format_system}",
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    "{project_hierarchy}",
    "{project_information_and_context}",
    "{file_context}",
    "{operating_principles}",
]

coder_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    "Act as an expert software developer.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("placeholder", "{examples}"),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)
