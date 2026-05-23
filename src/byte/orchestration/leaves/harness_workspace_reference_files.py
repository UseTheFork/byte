from typing import TYPE_CHECKING

from byte.files import FileService
from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class HarnessWorkspaceReferenceFiles(Leaf):
    """Harness leaf that renders reference files for the workspace."""

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        harness = prompt_assembler.get_state().get("harness", {})
        reference_files = harness.get("reference_files")
        file_service = prompt_assembler.get_app().make(FileService)

        lines = []

        if not reference_files:
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

        for file_path in reference_files:
            file_context = file_service.get_file_context(file_path)
            if file_context:
                lines.append(file_context.to_boundary())

        lines.append("```")
        lines.append(Section.end())

        return list_to_multiline_text(lines)
