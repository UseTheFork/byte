from typing import List

from pydantic import Field

from byte.orchestration.models.base_phase_model import BasePhaseModel, ToolType
from byte.support import MD, Section, SectionType
from byte.support.utils import list_to_multiline_text


class PhaseModel(BasePhaseModel):
    """Represents a single phase within a workflow, tracking its content, status, and associated tools or skills."""

    content: str
    note: List[str] = Field(default_factory=list)
    # Tools needed to complete this task
    tools: List[ToolType] = Field(default_factory=list)
    # Skills needed to complete this task
    skills: List[str] = Field(default_factory=list)

    tool_choice: dict[str, str] | str | None = Field(default=None)

    def to_pending_md(self) -> str:
        return list_to_multiline_text(
            [
                Section.sub_heading(f"Phase: {self.id}", 2),
                MD.bullet(f"- phase_status: {self.status}"),
                "",
                self.content,
                "",
                Section.end(),
            ]
        )

    def to_current_md(self) -> str:
        note_block = (
            [
                Section.sub_heading("Notes", 3),
                list_to_multiline_text([MD.bullet(note) for note in self.note]),
                "",
            ]
            if self.note
            else []
        )

        return list_to_multiline_text(
            [
                Section.start(SectionType.WORKFLOW_CURRENT_PHASE),
                f"- phase_id: phase-{self.id}",
                f"- phase_status: {self.status}",
                "",
                self.content,
                "",
                *note_block,
                Section.end(),
            ]
        )
