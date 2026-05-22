from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.specs import SpecLoaderService
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class SpecTasks(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        harness = prompt_assembler.get_state().get("harness", {})
        spec_name = harness.get("spec")

        spec_loader_service = prompt_assembler.get_app().make(SpecLoaderService)
        tasks = spec_loader_service.load_tasks(spec_name)

        if not tasks:
            return ""

        message_parts = [
            Section.start(SectionType.SPECIFICATION_TASKS),
        ]

        for phase in tasks:
            message_parts.append(phase.to_md())
            pass

        message_parts.extend(Section.end())

        return list_to_multiline_text(message_parts)
