from typing import List

from pydantic import Field

from byte.orchestration.models.base_phase_model import BasePhaseModel, ToolType
from byte.support import Section
from byte.support.utils import list_to_multiline_text


class PhaseModel(BasePhaseModel):
    """Represents a single phase within a workflow, tracking its content, status, and associated tools or skills."""

    content: str
    note: List[str] = Field(default_factory=list)
    # Tools needed to complete this task
    tools: List[ToolType] = Field(default_factory=list)
    # Skills needed to complete this task
    skills: List[str] = Field(default_factory=list)

    def to_pending_md(self) -> str:
        note_block = (
            [
                Section.sub_heading("Notes", 3),
                list_to_multiline_text(self.note),
                "",
            ]
            if self.note
            else []
        )

        return list_to_multiline_text(
            [
                Section.sub_heading(f"phase-{self.id}", 2, True),
                f"- phase_id: phase-{self.id}",
                f"- phase_status: {self.status}",
                "",
                self.content,
                "",
                *note_block,
                Section.end(),
            ]
        )
