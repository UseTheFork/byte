from pydantic import BaseModel, Field


class EditFormatConfig(BaseModel):
    """Configuration for edit format operations and shell command execution."""

    enable_shell_commands: bool = Field(
        default=False,
        description="Enable execution of shell commands from AI responses. When disabled, shell command blocks will not be executed.",
    )

    mask_message_count: int = Field(
        default=1,
        description="Number of recent AI messages to exclude from masking. Messages older than this count will have their SEARCH/REPLACE blocks removed to reduce token usage.",
    )
