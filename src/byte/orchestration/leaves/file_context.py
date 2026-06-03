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

        files = await file_service.generate_context_prompt()

        lines = []

        if not files:
            return ""

        if self.as_section:
            lines.extend(
                [
                    Section.start(SectionType.PROJECT_FILES),
                    "",
                    "Below is the current file state of the workspace. It includes all your changes as a result of previous tool calls."
                    "",
                    Section.important("You MUST trust this information as the current state of the files etc."),
                    "",
                ]
            )

        if files:
            editable_content = "\n".join(files)
            lines.extend(
                [
                    Section.sub_heading("Files", 2, True),
                    "",
                    "```",
                    f"{editable_content}",
                    "```",
                ]
            )

        if self.as_section:
            lines.append(Section.end())

        return list_to_multiline_text(lines)
