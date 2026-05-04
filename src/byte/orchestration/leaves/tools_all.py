from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text
from byte.tools import ToolRegistryService

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class ToolsAll(Leaf):
    def __init__(self, has_section: bool = False):
        self.has_section = has_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        tool_registry_service = prompt_assembler.get_app().make(ToolRegistryService)

        harness_tools = {name: tool for name, tool in tool_registry_service._tools.items() if tool.harness_invocable}
        tools_xml = tool_registry_service.tools_to_prompt_xml(harness_tools)

        if not tools_xml:
            return list_to_multiline_text(
                [
                    Section.start(SectionType.AVALIABLE_TOOLS),
                    "```",
                    "NO Tools avaliable.",
                    "```",
                ]
            )

        message_parts = [
            Section.start(SectionType.AVALIABLE_TOOLS),
            "```",
            tools_xml,
            "```",
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)
