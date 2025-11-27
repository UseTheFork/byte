from langchain_core.prompts import ChatPromptTemplate

from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary

coder_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    "Act as an expert software developer.",
                    Boundary.close(BoundaryType.ROLE),
                    "",
                    Boundary.open(BoundaryType.RULES),
                    "- Always use best practices when coding",
                    "- Respect and use existing conventions, libraries, etc that are already present in the code base",
                    "- Take requests for changes to the supplied code",
                    "- If the request is ambiguous, ask clarifying questions before proceeding",
                    "- Keep changes simple don't build more then what is asked for",
                    Boundary.close(BoundaryType.RULES),
                    "",
                    Boundary.open(BoundaryType.RESPONSE_FORMAT),
                    "{edit_format_system}",
                    Boundary.close(BoundaryType.RESPONSE_FORMAT),
                ]
            ),
        ),
        ("placeholder", "{examples}"),
        ("placeholder", "{project_inforamtion_and_context}"),
        ("placeholder", "{file_context}"),
        ("placeholder", "{masked_messages}"),
        ("user", "{processed_user_request}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)
