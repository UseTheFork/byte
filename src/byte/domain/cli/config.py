from dataclasses import dataclass


@dataclass(frozen=True)
class UIConfig:
	"""UI domain configuration with validation and defaults."""

	theme: str = "dark"
	show_file_context: bool = True
	code_theme: str = "default"
	dark_mode: bool = True
