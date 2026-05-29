from typing import TYPE_CHECKING

from byte.files import FileService
from byte.orchestration import HarnessStateUtils, Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class HarnessWorkspaceFiles(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        editable_files = HarnessStateUtils.get_editable_files(prompt_assembler.get_state())
        file_service = prompt_assembler.get_app().make(FileService)

        lines = []

        if not editable_files:
            return ""

        lines.extend(
            [
                Section.start(SectionType.PROJECT_FILES),
                "",
                "Below is the current file state of the workspace. It includes all your changes as a result of previous tool calls."
                "",
                Section.important("You MUST trust this information as the current state of the files etc."),
                "",
                Section.sub_heading("Editable Files", 2, True),
                "",
                "```",
            ]
        )

        for file_path in editable_files:
            file_context = file_service.get_file_context(file_path)
            if file_context:
                lines.append(file_context.to_boundary())

        lines.append("```")
        lines.append(Section.end())

        return list_to_multiline_text(lines)
