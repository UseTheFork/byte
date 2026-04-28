from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """ """

    success: bool = True
    result: str
    extra: dict = Field(default_factory=dict)
