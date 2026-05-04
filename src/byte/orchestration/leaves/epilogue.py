from typing import TYPE_CHECKING, List

from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class Epilogue(Leaf):
    def __init__(self, enforcements: List[str] = []):
        self.enforcements = enforcements

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        history_messages = prompt_assembler.get_state().get("history_messages", [])

        lines = [
            Section.start(SectionType.RESUME_FORMAT),
            "",
        ]

        # TODO: Should we consider plan here ?
        if not history_messages:
            lines.append("> **Remember**: This is your first response so you are starting at the FIRST step.")
        else:
            lines.extend(
                [
                    f"> **Remember**: This is a followup response. Make sure to consider the {Section.ref(SectionType.WORKFLOW)} section and plan accordingly."
                ]
            )

        return list_to_multiline_text(lines)
