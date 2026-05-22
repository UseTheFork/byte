from typing import TYPE_CHECKING, List

from byte.orchestration import Leaf, PhaseModel, PhaseUtils
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class Epilogue(Leaf):
    def __init__(self, enforcements: List[str] = []):
        self.enforcements = enforcements

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        scratch_messages = prompt_assembler.get_state().get("scratch_messages", [])

        lines = [
            Section.start(SectionType.RESUME_FORMAT),
            "",
        ]

        if self.enforcements:
            lines.extend(self.enforcements)

        if PhaseUtils.is_workflow_agent(prompt_assembler.get_state()):
            pending_phase = PhaseUtils.get_pending_phase(prompt_assembler.get_state())
            if pending_phase is not None and isinstance(pending_phase, PhaseModel):
                lines.append(
                    f"> **Remember**: This is a followup response. Make sure to consider the {Section.ref(SectionType.WORKFLOW_CURRENT_PHASE)} section and plan accordingly."
                )
                lines.append(pending_phase.to_current_md())
        else:
            if not scratch_messages:
                lines.append("> **Remember**: This is your first response so you are starting at the FIRST step.")
            else:
                lines.append(
                    f"> **Remember**: This is a followup response. Make sure to consider the {Section.ref(SectionType.WORKFLOW)} section and plan accordingly."
                )

        return list_to_multiline_text(lines)
