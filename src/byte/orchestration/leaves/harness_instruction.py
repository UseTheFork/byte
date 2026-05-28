from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class HarnessInstruction(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        harness = prompt_assembler.get_state().get("harness", {})
        instruction = str(harness.get("instruction"))

        message_parts = [
            Section.start(SectionType.USER_INPUT),
            "```",
            instruction,
            "```",
            "",
            "You **MUST** consider the user instruction before proceeding (if not empty).",
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)
