import shutil
from typing import Optional

import yaml
from rich.console import Console

from byte.core.config.config import BYTE_CACHE_DIR, BYTE_CONFIG_FILE


class FirstBootInitializer:
	"""Handle first-time setup and configuration for Byte.

	Detects if this is the first run and guides users through initial
	configuration, creating necessary files and directories.
	Usage: `initializer = FirstBootInitializer()`
			`await initializer.run_if_needed()`
	"""

	_console: Console | None = None

	# Default configuration template for first boot
	# This will be written to .byte/config.yaml
	CONFIG_TEMPLATE = {
		"llm": {
			"model": "anthropic",
		},
		"lint": {
			"enabled": False,
			"commands": [
				{
					"command": "uv run ruff format --force-exclude --respect-gitignore",
					"extensions": [".py"],
				}
			],
		},
		"files": {
			"ignore": [
				".ruff_cache",
				".idea",
				".venv",
				".env",
				".git/",
				"__pycache__",
				"node_modules",
			],
			"watch": {
				"enabled": False,
			},
		},
		"web": {
			"enabled": False,
			"chrome_binary_location": "/usr/bin/google-chrome",
		},
		"edit_format": {
			"enable_shell_commands": False,
		},
		# "mcp": [
		# {
		# "name": "docs-mcp-server",
		# "connection": {
		# "url": "https://docs-mcp-server.mcp.dango.isdelicio.us/mcp",
		# "transport": "streamable_http",
		# },
		# "agents": {
		# "ask": {
		# "include": ["search_docs", "list_libraries"],
		# },
		# "research": {
		# "include": ["search_docs", "list_libraries"],
		# },
		# },
		# },
		# ],
	}

	def __init__(self):
		pass

	def is_first_boot(self) -> bool:
		"""Check if this is the first time Byte is being run.

		Usage: `if await initializer.is_first_boot(): ...`
		"""
		return not BYTE_CONFIG_FILE.exists()

	def run_if_needed(self) -> bool:
		"""Run initialization flow if this is the first boot.

		Returns True if initialization was performed, False if skipped.
		Usage: `initialized = await initializer.run_if_needed()`
		"""
		if not self.is_first_boot():
			return False

		self._run_initialization()
		return True

	def _run_initialization(self) -> None:
		"""Perform first-boot initialization steps.

		Creates the default configuration file from the template.
		"""

		self._console = Console()

		# Display welcome message for first boot
		self.print_info("\n[bold cyan]Welcome to Byte![/bold cyan]")
		self.print_info("Setting up your development environment...\n")

		# Set up all Byte directories
		self._setup_byte_directories()

		# Initialize web configuration
		config = self._init_web(self.CONFIG_TEMPLATE)

		# Write the configuration template to the YAML file
		with open(BYTE_CONFIG_FILE, "w") as f:
			yaml.dump(
				config,
				f,
				default_flow_style=False,
				sort_keys=False,
				allow_unicode=True,
			)

		self.print_success(f"Created configuration file at {BYTE_CONFIG_FILE}\n")

	def _setup_byte_directories(self) -> None:
		"""Set up all necessary Byte directories.

		Creates .byte, .byte/conventions, and .byte/cache directories.
		Usage: `initializer._setup_byte_directories()`
		"""

		# Ensure the main .byte directory exists
		BYTE_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

		# Create conventions directory for style guides and project conventions
		conventions_dir = BYTE_CONFIG_FILE.parent / "conventions"
		conventions_dir.mkdir(exist_ok=True)

		# Create context directory for style guides and project context
		context_dir = BYTE_CONFIG_FILE.parent / "context"
		context_dir.mkdir(exist_ok=True)

		# Create cache directory for temporary files
		BYTE_CACHE_DIR.mkdir(exist_ok=True)

		self.print_success("Created Byte directories")

	def _init_web(self, config: dict) -> dict:
		"""Initialize web configuration by detecting Chrome or Chromium binary.

		Attempts to locate google-chrome first, then falls back to chromium.
		Updates the chrome_binary_location in the web config section.
		Usage: `config = initializer._init_web(config)`
		"""
		chrome_path = self.find_binary("google-chrome")
		if chrome_path is None:
			chrome_path = self.find_binary("chromium")

		if chrome_path is not None:
			config["web"]["chrome_binary_location"] = chrome_path
			config["web"]["enabled"] = True
			browser_name = "Chrome" if "chrome" in chrome_path else "Chromium"
			self.print_success(f"Found {browser_name} at {chrome_path}")
			self.print_success("Web commands enabled\n")
		else:
			self.print_warning("Chromium binary not found")
			self.print_warning("Web commands are disabled\n")

		return config

	def find_binary(self, binary_name: str) -> Optional[str]:
		"""Find the full path to a binary using which.

		Returns the absolute path to the binary if found, None otherwise.
		Usage: `chrome_path = initializer.find_binary("google-chrome")`
		Usage: `python_path = initializer.find_binary("python3")` -> "/usr/bin/python3"
		"""
		return shutil.which(binary_name)

	def print_info(self, message: str) -> None:
		"""Print an informational message with two leading spaces for alignment.

		Usage: `initializer.print_info("Configuring settings...")`
		"""
		if self._console:
			self._console.print(f"  {message}")

	def print_success(self, message: str) -> None:
		"""Print a success message with a green checkmark.

		Usage: `initializer.print_success("Configuration saved")`
		"""
		if self._console:
			self._console.print(f"[green]✓[/green] {message}")

	def print_error(self, message: str) -> None:
		"""Print an error message with a red X.

		Usage: `initializer.print_error("Failed to save configuration")`
		"""
		if self._console:
			self._console.print(f"[red]✗[/red] {message}")

	def print_warning(self, message: str) -> None:
		"""Print a warning message with a yellow exclamation mark.

		Usage: `initializer.print_warning("Chrome not found, web commands disabled")`
		"""
		if self._console:
			self._console.print(f"[yellow]⚠[/yellow] {message}")
