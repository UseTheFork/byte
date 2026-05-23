from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text
from byte.tools import ToolRegistryService

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class ToolsLoaded(Leaf):
    def __init__(self, as_section: bool = False):
        self.as_section = as_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:

        tool_registry_service = prompt_assembler.get_app().make(ToolRegistryService)
        tools = prompt_assembler.get_tools()

        if not tools:
            return ""

        harness_tools = {tool.name: tool for tool in tools}
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
            Section.important(
                "These are the ONLY tools you are allowed to use. Any other tool calls will be rejected."
            ),
            "```",
            tools_xml,
            "```",
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)
