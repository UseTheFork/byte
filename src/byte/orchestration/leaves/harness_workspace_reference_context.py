from typing import TYPE_CHECKING

from byte.knowledge import SessionContextService
from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class HarnessWorkspaceReferenceContext(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        harness = prompt_assembler.get_state().get("harness", {})
        reference_context = harness.get("reference_context")
        session_context_service = prompt_assembler.get_app().make(SessionContextService)

        lines = []

        if not reference_context:
            return ""

        lines.extend(
            [
                Section.start(SectionType.PROJECT_REFERENCE),
                "",
                "Below are files for reference only. Any edits to these files will be rejected",
                "",
                "```",
            ]
        )

        for context_key in reference_context:
            file_context = session_context_service.get_context(context_key)
            if file_context:
                lines.append(file_context.to_boundary())

        lines.append("```")
        lines.append(Section.end())

        return list_to_multiline_text(lines)
