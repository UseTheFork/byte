from langchain_core.prompts.chat import ChatPromptTemplate

from byte.agent.prompt_leaves import preamble
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

compression_user_template = [
    "{messages}",
    "",
    "You **MUST** consider the conversation history before proceeding (if not empty).",
    "",
    Boundary.open(BoundaryType.TASK),
    "When the conversation history grows too large, you will be invoked to distill the entire history into a concise, structured XML snapshot. This snapshot is CRITICAL, as it will become the agent's *only* memory of the past. The agent will resume its work based solely on this snapshot. All crucial details, plans, errors, and user directives MUST be preserved.",
    Boundary.close(BoundaryType.TASK),
    "",
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- Preserve ALL critical information: user requests, decisions made, work completed, pending tasks, errors encountered, and solutions applied",
    "- Maintain chronological order of significant events",
    "- Include specific file paths, function names, and code changes that were discussed or implemented",
    "- Capture the current state of the project and what the agent was working on",
    "- Preserve user preferences, constraints, and special instructions given during the conversation",
    "- Remove redundant back-and-forth, but keep the essence of important discussions",
    "- Compress verbose explanations while retaining key insights and decisions",
    "- Use concise language without losing meaning or context",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    Boundary.open(BoundaryType.CRITICAL_REQUIREMENTS),
    "The snapshot MUST be comprehensive enough that:",
    "- The agent can resume work exactly where it left off",
    "- No critical context or decisions are lost",
    "- The user doesn't need to repeat important information",
    "- All pending tasks and blockers are clearly documented",
    Boundary.close(BoundaryType.CRITICAL_REQUIREMENTS),
    "",
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "Structure your snapshot using XML boundaries to organize information:",
    "- Use appropriate boundary types (TASK, CONTEXT, ERROR, etc.) to categorize information",
    "- Group related information together logically",
    "- Use clear, scannable headings and bullet points",
    "- Include code snippets where relevant to preserve technical context",
    "- Maintain a balance between completeness and conciseness",
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    "",
    Boundary.open(BoundaryType.GOAL),
    "Create a compressed memory snapshot that preserves all essential context while",
    "reducing token count, enabling the agent to continue its work seamlessly.",
    Boundary.close(BoundaryType.GOAL),
]

compression_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    preamble(),
                    "You are a specialized system component responsible for distilling chat history into a structured State Snapshot.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)
