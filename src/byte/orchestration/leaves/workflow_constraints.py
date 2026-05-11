from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support.section import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class WorkflowConstraints(Leaf):
    def __init__(self, extra_constraints: list = []):
        self.extra_constraints = extra_constraints

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        """ """

        constraints = [
            Section.start(SectionType.WORKFLOW_CONSTRAINTS),
            "- Never use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
        ]

        constraints.extend(self.extra_constraints)

        constraints.append(Section.end())

        return list_to_multiline_text(constraints)
