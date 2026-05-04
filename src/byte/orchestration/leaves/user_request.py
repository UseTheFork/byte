from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class UserRequest(Leaf):
    def __init__(self, has_section: bool = False):
        self.has_section = has_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        """Gather reinforcement messages from various domains."""
        user_request = prompt_assembler.get_state().get("user_request", "")

        message_parts = [
            Section.start(SectionType.USER_INPUT),
            "```",
            user_request,
            "```",
            "",
            "You **MUST** consider the user input before proceeding (if not empty).",
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)
