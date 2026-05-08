from typing import TYPE_CHECKING

from byte.constitution import ConstitutionService
from byte.orchestration import Leaf

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class Constitution(Leaf):
    def __init__(self, as_section: bool = True):
        self.as_section = as_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        constitution_service = prompt_assembler.get_app().make(ConstitutionService)
        constitution_md = constitution_service.get_constitution().to_markdown()

        return constitution_md
