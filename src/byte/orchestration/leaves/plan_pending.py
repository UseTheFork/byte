from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class PlanPending(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        plan = prompt_assembler.get_state().get("plan")
        if not plan:
            return ""

        message_parts = [
            Section.start(SectionType.PLAN),
            "Plan steps:",
            "",
        ]

        for step in sorted(plan, key=lambda s: s.order):
            status = step.status

            lines = [
                f"## [{step.id}] ({status})",
                f"{step.content}",
            ]
            message_parts.extend(lines)

        message_parts.append(Section.end())
        return list_to_multiline_text(message_parts)
