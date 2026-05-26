from typing import TYPE_CHECKING

from byte.constitution import ConstitutionService
from byte.files import FileService
from byte.orchestration import Leaf

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class Constitution(Leaf):
    def __init__(self, is_filtered: bool = True):
        self.is_filtered = is_filtered

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:

        constitution_service = prompt_assembler.get_app().make(ConstitutionService)

        filtered = None
        if self.is_filtered:
            file_service = prompt_assembler.get_app().make(FileService)
            context_files = file_service.list_files()
            filtered = [f.path for f in context_files] if context_files else None

        constitution_md = constitution_service.get_constitution_for_path(filtered)  # ty:ignore[invalid-argument-type]
        if not constitution_md:
            return ""

        return constitution_md.to_markdown()
