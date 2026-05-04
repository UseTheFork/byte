from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class ConversationHistory(Leaf):
    def __init__(self, has_section: bool = False):
        self.has_section = has_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        messages = prompt_assembler.get_state().get("history_messages", [])
        messages = prompt_assembler.get_agent_node().filter_message_history(messages)  # ty:ignore[invalid-argument-type]

        # Create masked_messages list identical to messages except for processed AIMessages

        masked_messages = [
            Section.start(SectionType.CONVERSATION_HISTORY),
            "",
            "Below is the conversation history between Byte agents and the user.",
            "",
            f"Messages are wrapped in XML tags corresponding to their type (e.g. `{Boundary.open(BoundaryType.AGENT_MESSAGE)}`, `{Boundary.open(BoundaryType.USER_MESSAGE)}`, `{Boundary.open(BoundaryType.TOOL_CALL)}`).",
            "",
            "```",
        ]

        if not messages:
            masked_messages.extend(
                [
                    "The conversation history is empty.",
                    "```",
                    Section.end(),
                ]
            )
            return list_to_multiline_text(masked_messages)

        for message in messages:
            masked_messages.append(message.text)

        masked_messages.extend(
            [
                "```",
                "",
                Section.important("You **MUST** consider the conversation history before proceeding."),
                Section.end(),
            ]
        )

        return list_to_multiline_text(masked_messages)
