from datetime import UTC, datetime
from typing import Annotated, List, Literal, Type

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from byte.node.base_agent_node import BaseAgentNode
from byte.support import Section
from byte.support.utils import list_to_multiline_text
from byte.tools.base_tool import BaseTool

TypeSerializer = PlainSerializer(lambda t: t.__name__ if isinstance(t, type) else t, return_type=str)

ToolType = Annotated[Type[BaseTool], TypeSerializer]
AgentType = Annotated[Type[BaseAgentNode], TypeSerializer]


class PhaseModel(BaseModel):
    """Represents a single phase within a workflow, tracking its content, status, and associated tools or skills."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    content: str
    note: List[str] = Field(default_factory=list)
    # Tools needed to complete this task
    tools: List[ToolType] = Field(default_factory=list)
    # Skills needed to complete this task
    skills: List[str] = Field(default_factory=list)
    status: Literal["pending", "in_progress", "blocked", "completed"] = Field(default="pending")
    completion_mode: Literal["auto", "confirm"] = Field(default="auto")
    agent: AgentType | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

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
