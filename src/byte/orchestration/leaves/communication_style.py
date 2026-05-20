from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support.section import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class CommunicationStyle(Leaf):
    def __init__(self, extra_styles: list = [], verbose: bool = False):
        self.extra_styles = extra_styles
        self.verbose = verbose

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:

        constraints = [
            Section.start(SectionType.COMMUNICATION_STYLE),
        ]

        if not self.verbose:
            constraints.append("  - Under 4 lines of text (tool use doesn't count)")

        constraints.extend(
            [
                "  - ALWAYS think and respond in the same spoken language the prompt was written in.",
                """  - No preamble ("Here's...", "I'll...")""",
                """  - No postamble ("Let me know...", "Hope this helps...")""",
                "  - No emojis ever",
                "  - Use rich Markdown formatting (headings, bullet lists, tables, code fences) for any multi-sentence or explanatory answer; only use plain unformatted text if the user explicitly asks.",
            ]
        )

        constraints.extend(self.extra_styles)

        constraints.append(Section.end())

        return list_to_multiline_text(constraints)
