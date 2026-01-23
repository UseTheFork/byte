from pydantic import BaseModel, Field


class PresetsConfig(BaseModel):
    id: str = Field(description="Unique identifier for the preset, used in /preset <id> command")
    read_only_files: list[str] = Field(default_factory=list, description="Files to add to read-only context")
    editable_files: list[str] = Field(default_factory=list, description="Files to add to editable context")
    conventions: list[str] = Field(default_factory=list, description="Convention files to load")
    prompt: str | None = Field(default=None, description="Preset prompt to load into chat input")
    load_on_boot: bool = Field(default=False, description="Automatically load this preset when byte starts")
