from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax

from byte.core.service.base_service import Service


# AI: should `console` in the below be a property? AI?
class ConsoleService(Service):
	""" """

	_console: Console

	async def boot(self, **kwargs) -> None:
		self._console = Console()

	@property
	def console(self):
		return self._console

	@property
	def width(self) -> int:
		"""Get the current console width in characters.

		Usage: `max_width = console_service.width`
		"""
		return self._console.width

	@property
	def height(self) -> int:
		"""Get the current console height in lines.

		Usage: `max_height = console_service.height`
		"""
		return self._console.height

	def print(self, *args, **kwargs) -> None:
		"""Print to console with Rich formatting support.

		Proxies directly to the underlying Rich Console.print() method,
		supporting all Rich markup, styling, and formatting features.

		Usage:
			`service.print("Hello, world!")`
			`service.print("[success]Operation complete[/success]")`
			`service.print(panel, syntax, table)`

		Args:
			*args: Objects to print (strings, Rich renderables, etc.)
			**kwargs: Keyword arguments passed to Console.print()
		"""
		self._console.print(*args, **kwargs)

	def syntax(self, *args, **kwargs):
		"""Create a themed Syntax component for code display.

		Applies the configured syntax highlighting theme from application
		settings while allowing caller to override specific options.

		Usage:
			`syntax = service.syntax("def foo(): pass", "python")`
			`syntax = service.syntax(code, "python", line_numbers=False)`

		Args:
			*args: Positional arguments passed to Rich's Syntax constructor
			**kwargs: Keyword arguments passed to Syntax, with theme defaulted

		Returns:
			Syntax: Configured Rich Syntax component ready for rendering
		"""
		kwargs.setdefault("theme", self._config.cli.syntax_theme)
		return Syntax(*args, **kwargs)

	def panel(self, *args, **kwargs):
		""" """
		kwargs.setdefault("title_align", "left")
		kwargs.setdefault("subtitle_align", "left")
		kwargs.setdefault("border_style", "inactive_border")
		return Panel(*args, **kwargs)

	def rule(self, *args, **kwargs):
		""" """
		kwargs.setdefault("characters", "-")
		kwargs.setdefault("align", "left")
		return Rule(*args, **kwargs)
