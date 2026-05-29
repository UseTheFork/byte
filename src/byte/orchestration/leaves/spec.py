from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.specs import SpecLoaderService
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class Spec(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        harness = prompt_assembler.get_state().get("harness", {})
        spec_name = harness.get("spec")

        if not spec_name:
            return ""

        spec_loader_service = prompt_assembler.get_app().make(SpecLoaderService)
        spec = spec_loader_service.get_spec(spec_name)

        if not spec:
            return ""

        message_parts = [Section.start(SectionType.SPECIFICATION), spec.to_md()]

        message_parts.extend(Section.end())

        return list_to_multiline_text(message_parts)
