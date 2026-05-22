from typing import TYPE_CHECKING

from byte.orchestration import Leaf, OrchestrationEvents
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class OperatingPrinciples(Leaf):
    def __init__(self, has_section: bool = False):
        self.has_section = has_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        """Gather project hierarchy for LLM understanding of project structure.

        Uses FileService to generate a concise tree-like representation
        of the project's directory structure and important files.

        Returns:
                List containing a single HumanMessage with formatted project hierarchy

        Usage: `hierarchy_messages = await self._gather_project_hierarchy()`
        """

        reinforcement_payload = await prompt_assembler.emit(
            OrchestrationEvents.GatherReinforcement(
                model=prompt_assembler.get_model_schema().model,
                provider=prompt_assembler.get_model_schema().provider,
                agent=prompt_assembler.get_agent_node().name,
                reinforcement=[],
            )
        )
        reinforcement_messages = reinforcement_payload.reinforcement

        message_parts = []

        # Add reinforcement section if there are messages
        if reinforcement_messages:
            reinforcement_parts = [
                "",
                Section.start(SectionType.OPERATING_PRINCIPLES),
                Section.important("You **MUST** follow these Operating Principles"),
                *reinforcement_messages,
                Section.end(),
            ]

            message_parts.extend(reinforcement_parts)

        return list_to_multiline_text(message_parts)
