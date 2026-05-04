from datetime import datetime
from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class ProjectEnvironment(Leaf):
    def __init__(self, has_section: bool = False):
        self.has_section = has_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        root_path = prompt_assembler.get_app().root_path()

        # TODO: https://github.com/charmbracelet/crush/blob/64c47cbbb3f0825432876786fb72737089732f55/internal/agent/templates/coder.md.tpl
        message_parts = [
            Section.start(SectionType.PROJECT_ENVIRONMENT),
            f"Working directory: {root_path}",
            f"Today's date: {datetime.now().strftime('%Y-%m-%d')}",
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)
