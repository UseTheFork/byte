from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """ """

    result: dict
    extra: dict = Field(default_factory=dict)
