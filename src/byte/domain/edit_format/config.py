from pydantic import BaseModel, Field


class EditFormatConfig(BaseModel):
	"""Configuration for edit format operations and shell command execution."""

	enable_shell_commands: bool = Field(
		default=False,
		description="Enable execution of shell commands from AI responses. When disabled, shell command blocks will not be executed.",
	)
