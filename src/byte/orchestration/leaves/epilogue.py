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
        scratch_messages = prompt_assembler.get_state().get("scratch_messages", [])

        lines = [
            Section.start(SectionType.RESUME_FORMAT),
            "",
        ]

        # # TODO: Should we consider plan here ?
        if not scratch_messages:
            lines.append("> **Remember**: This is your first response so you are starting at the FIRST step.")
        else:
            lines.extend(
                [
                    f"> **Remember**: This is a followup response. Make sure to consider the {Section.ref(SectionType.WORKFLOW)} section and plan accordingly."
                ]
            )

        return list_to_multiline_text(lines)


#             # plan = prompt_assembler.get_state().get("plan")
# if plan:
#     current_step = next(
#         (s for s in sorted(plan, key=lambda s: s.order) if s.status in ("pending", "in_progress")),
#         None,
#     )
#     if current_step:
#         lines.append(f"> **Current Step**: [{current_step.id}] (in_progress) — {current_step.content}")
#         if current_step.note:
#             lines.extend([f">   - {note}" for note in current_step.note])
