from typing import TYPE_CHECKING

from byte.orchestration import Leaf, PhaseModel, PhaseUtils
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class WorkflowPending(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        workflow_phases = PhaseUtils.get_workflow_phases(prompt_assembler.get_state())
        if not workflow_phases:
            return ""

        message_parts = [
            Section.start(SectionType.WORKFLOW_PHASES),
            "",
        ]

        for step in workflow_phases.values():
            if isinstance(step, PhaseModel):
                message_parts.append(step.to_pending_md())

        message_parts.append(Section.end())
        return list_to_multiline_text(message_parts)
