from datetime import UTC, datetime
from typing import Annotated, List, Literal, Type

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from byte.node.base_agent_node import BaseAgentNode
from byte.tools.base_tool import BaseTool

TypeSerializer = PlainSerializer(lambda t: t.__name__ if isinstance(t, type) else t, return_type=str)

ToolType = Annotated[Type[BaseTool], TypeSerializer]
AgentType = Annotated[Type[BaseAgentNode], TypeSerializer]


class PlanStep(BaseModel):
    """Represents a single step within a plan, tracking its content, status, and associated tools or skills."""

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
    order: int
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
