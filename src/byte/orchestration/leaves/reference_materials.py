from typing import TYPE_CHECKING

from byte.orchestration import Leaf, OrchestrationEvents
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class ReferenceMaterials(Leaf):
    def boot(self, has_section: bool = False):
        self.has_section = has_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        """Gather project context including conventions and session documents.

        Emits GATHER_PROJECT_CONTEXT event and formats the response into
        structured sections for conventions and session context.

        Returns:
                List containing a single HumanMessage with formatted project context

        Usage: `context_messages = await self._gather_project_context()`
        """

        project_context = await prompt_assembler.emit(OrchestrationEvents.GatherProjectContext())

        # TODO: Add a descrption here.
        project_information_and_context = [
            Section.start(SectionType.REFERENCE_MATERIALS),
            "",
        ]

        session_docs = project_context.session_docs
        if session_docs:
            session_docs = "\n\n".join(session_docs)
            project_information_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "session"}),
                    f"{session_docs}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        if not project_context.conventions and not project_context.session_docs:
            return ""

        project_information_and_context.append(Section.end())

        return list_to_multiline_text(project_information_and_context)
