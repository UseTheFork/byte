from typing import Literal

from pydantic import BaseModel, Field


class CLIConfig(BaseModel):
    """CLI domain configuration with validation and defaults."""

    ui_theme: Literal["mocha", "macchiato", "latte", "frappe"] = Field(
        default="mocha",
        description="Catppuccin theme variant for the CLI interface (mocha/macchiato are dark, latte is light, frappe is cool dark)",
    )
    syntax_theme: Literal["github-dark", "bw", "sas", "staroffice", "xcode", "monokai", "lightbulb", "rrt"] = Field(
        default="monokai",
        description="Pygments theme for code block syntax highlighting in CLI output",
    )
