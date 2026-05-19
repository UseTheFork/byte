from datetime import UTC, datetime
from typing import Annotated, Literal, Type

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from byte.node import BaseNode
from byte.support import Str
from byte.tools.base_tool import BaseTool

TypeSerializer = PlainSerializer(lambda t: t.__name__ if isinstance(t, type) else t, return_type=str)

ToolType = Annotated[Type[BaseTool], TypeSerializer]
NodeType = Annotated[Type[BaseNode], TypeSerializer]


class BasePhaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    status: Literal["pending", "in_progress", "blocked", "completed"] = Field(default="pending")

    executed_by: NodeType

    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def get_executed_by(self) -> str:
        return Str.class_to_snake_case(self.executed_by)
