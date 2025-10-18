from typing import Optional

import click
from rich import get_console
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


# Credits to https://github.com/gbPagano/rich_menu/blob/main/rich_menu/menu.py
class Menu:
	def __init__(
		self,
		*options: str,
		start_index: int = 0,
		title: str = "",
		color: str = "secondary",
		selected_color: str = "primary",
		transient: bool = False,
		console: Optional[Console] = None,
	):
		self.options = options
		self.index = start_index
		self.title = title
		self.color = color
		self.selected_color = selected_color
		self.transient = transient
		self.selected_options = []

		self.selection_char = "›"  # noqa: RUF001

		self.border_style = "inactive_border"

		self.console = console if console is not None else get_console()
		self.live: Optional[Live] = None

	def _get_click(self) -> str | None:
		match click.getchar():
			case "\r":
				return "enter"
			case "\x1b[B" | "s" | "S" | "àP" | "j":
				return "down"
			case "\x1b[A" | "w" | "W" | "àH" | "k":
				return "up"
			case "\x1b[D" | "a" | "A" | "àK" | "h":
				return "left"
			case "\x1b[C" | "d" | "D" | "àM" | "l":
				return "right"
			case " " | "\x0d":
				return "space"
			case "\x1b":
				return "exit"
			case _:
				return None

	def _update_index(self, key: str | None) -> None:
		if key == "down":
			self.index += 1
		elif key == "up":
			self.index -= 1

		if self.index > len(self.options) - 1:
			self.index = 0
		elif self.index < 0:
			self.index = len(self.options) - 1

	@property
	def _group(self) -> Panel:
		menu = Text(justify="left")

		# Selection char is always in front when current
		# Circle prefix shows selection state (filled when selected, empty otherwise)
		selection_prefix = f"{self.selection_char} "
		empty_prefix = "  "

		for idx, option in enumerate(self.options):
			if idx == self.index:
				menu.append(
					Text.assemble(
						Text(selection_prefix, self.color),
						Text("◼  ", self.selected_color),
						Text(option + "\n", self.selected_color),
					)
				)
			else:
				# Not current item - no selection char
				if option in self.selected_options:
					# Not current but selected - filled circle
					menu.append(
						Text.assemble(
							Text(empty_prefix),
							Text("◼  ", self.selected_color),
							Text(option + "\n", self.selected_color),
						)
					)
				else:
					# Not current and not selected - hollow circle
					menu.append(Text.assemble(Text(empty_prefix), Text("◻  "), Text(option + "\n")))
		menu.rstrip()

		return Panel(
			menu,
			title=f"[text]{self.title}[/text]",
			title_align="left",
			border_style=self.border_style,
		)

	def select(self, esc: bool = True) -> str | None:
		with Live(self._group, auto_refresh=False, console=self.console, transient=self.transient) as live:
			self.live = live
			live.update(self._group, refresh=True)
			while True:
				try:
					key = self._get_click()
					if key == "enter":
						break
					elif key == "exit" and esc:
						self.border_style = "danger"
						live.update(self._group, refresh=True)
						return None

					self._update_index(key)
					live.update(self._group, refresh=True)
				except (KeyboardInterrupt, EOFError):
					self.border_style = "danger"
					live.update(self._group, refresh=True)
					return None

		return self.options[self.index]

	def multiselect(
		self,
		esc: bool = True,
	) -> list[str] | None:
		self.selected_options = []
		with Live(self._group, auto_refresh=False, console=self.console, transient=self.transient) as live:
			self.live = live
			live.update(self._group, refresh=True)
			while True:
				try:
					key = self._get_click()
					if key == "enter":
						break
					elif key == "exit" and esc:
						self.border_style = "danger"
						live.update(self._group, refresh=True)
						self.selected_options = None
						break
					elif key == "down" or key == "up":
						self._update_index(key)
					elif key == "space":
						if self.options[self.index] in self.selected_options:
							self.selected_options.remove(self.options[self.index])
						else:
							self.selected_options.append(self.options[self.index])

					live.update(self._group, refresh=True)
				except (KeyboardInterrupt, EOFError):
					self.border_style = "danger"
					live.update(self._group, refresh=True)
					self.selected_options = None
					break

		return self.selected_options
