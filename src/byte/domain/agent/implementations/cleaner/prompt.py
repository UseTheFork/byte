from langchain_core.prompts.chat import ChatPromptTemplate

from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary

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
                    "",
                    Boundary.open(BoundaryType.RULES),
                    "- Remove: marketing fluff, legal boilerplate, repetitive examples, excessive formatting",
                    "- Preserve: technical details, version numbers, API signatures, configuration values, caveats",
                    "- Restructure: group related concepts, use clear hierarchy, prefer lists over prose",
                    "- Maintain: original terminology, code snippets, important warnings or notes",
                    "- Prioritize: actionable information over background context",
                    Boundary.close(BoundaryType.RULES),
                    "",
                    Boundary.open(BoundaryType.RESPONSE_FORMAT),
                    "Return only the distilled content without meta-commentary.",
                    "Use markdown structure (headers, lists, code blocks) when it improves clarity.",
                    "Keep the output 30-70% of the original length while retaining 100% of the value.",
                    Boundary.close(BoundaryType.RESPONSE_FORMAT),
                ]
            ),
        ),
        ("placeholder", "{messages}"),
    ]
)
