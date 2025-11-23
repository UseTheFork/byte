from pydantic import BaseModel, Field


class PresetsConfig(BaseModel):
    id: str = Field(description="Unique identifier for the preset, used in /preset <id> command")
    read_only_files: list[str] = Field(default_factory=list, description="Files to add to read-only context")
    editable_files: list[str] = Field(default_factory=list, description="Files to add to editable context")
    conventions: list[str] = Field(default_factory=list, description="Convention files to load")
