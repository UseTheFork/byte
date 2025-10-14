from typing import Literal

from pydantic import BaseModel, Field


class CLIConfig(BaseModel):
	"""CLI domain configuration with validation and defaults."""

	ui_theme: str = Field(
		default="dark",
		description="Theme for the general CLI interface (controls colors, formatting, and visual presentation)",
	)
	syntax_theme: Literal["github-dark", "bw", "sas", "staroffice", "xcode", "monokai", "lightbulb", "rrt"] = Field(
		default="monokai",
		description="Pygments theme for code block syntax highlighting in CLI output",
	)
