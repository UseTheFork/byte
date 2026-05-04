from typing import TYPE_CHECKING

from byte.files import FileService
from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class FileContext(Leaf):
    def __init__(self, as_section: bool = True):
        self.as_section = as_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        """ """
        file_service = prompt_assembler.get_app().make(FileService)

        read_only_files, editable_files = await file_service.generate_context_prompt_with_line_numbers()

        lines = []

        if not read_only_files and not editable_files:
            return ""

        if self.as_section:
            lines.extend(
                [
                    Section.start(SectionType.PROJECT_FILES),
                    "",
                    "Below is the current file state of the project. It includes all your changes as a result of previous tool calls that have been masked for brevity."
                    "",
                    Section.important("You MUST trust this information as the current state of the files etc."),
                    "",
                ]
            )

        if read_only_files:
            read_only_content = "\n".join(read_only_files)
            lines.extend(
                [
                    Section.sub_heading("Read Only Files", 3),
                    "Any edits to these files will be rejected",
                    "",
                    "```",
                    f"{read_only_content}",
                    "```",
                ]
            )

        if editable_files:
            editable_content = "\n".join(editable_files)
            lines.extend(
                [
                    Section.sub_heading("Editable Files", 3),
                    "",
                    "```",
                    f"{editable_content}",
                    "```",
                ]
            )

        if self.as_section:
            lines.append(Section.end())

        return list_to_multiline_text(lines)
