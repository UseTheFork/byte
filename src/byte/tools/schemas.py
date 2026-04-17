from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """ """

    result: str
    extra: dict = Field(default_factory=dict)
