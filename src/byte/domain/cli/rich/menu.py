from typing import Optional

import click
from rich import get_console
from rich.align import AlignMethod
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
		color: str = "primary",
		align: AlignMethod = "left",
		selection_char: str = ">",
		selected_char: str = "*",
		selected_color: str = "primary",
		highlight_color: str = "",
		console: Optional[Console] = None,
	):
		self.options = options
		self.index = start_index
		self.title = title
		self.color = color
		self.align = align
		self.selection_char = selection_char
		self.highlight_color = highlight_color
		self.selected_char = selected_char
		self.selected_color = selected_color
		self.selected_options = []

		self.console = console if console is not None else get_console()

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

		current = Text(self.selection_char + " ", self.color)
		not_selected = Text(" " * (len(self.selection_char) + 1))
		selected = Text(self.selected_char + " ", self.selected_color)

		for idx, option in enumerate(self.options):
			if idx == self.index and option in self.selected_options:  # is current selected in multiple selection mode
				menu.append(Text.assemble(current, Text(option + "\n", self.selected_color)))
			elif idx == self.index:  # is selected in single mode
				menu.append(Text.assemble(current, Text(option + "\n", self.highlight_color)))
			elif option in self.selected_options:  # is selected in multiple selection mode
				menu.append(Text.assemble(selected, Text(option + "\n", self.selected_color)))
			else:
				menu.append(Text.assemble(not_selected, option + "\n"))
		menu.rstrip()

		return Panel(
			menu,
			title=self.title,
			title_align="left",
			border_style="inactive_border",
		)

	def _clean_menu(self):
		for _ in range(len(self.options) + 3):
			print("\x1b[A\x1b[K", end="")

	def ask(self, esc: bool = True) -> str:
		with Live(self._group, auto_refresh=False, console=self.console) as live:
			live.update(self._group, refresh=True)
			while True:
				try:
					key = self._get_click()
					if key == "enter":
						break
					elif key == "exit" and esc:
						exit()

					self._update_index(key)
					live.update(self._group, refresh=True)
				except (KeyboardInterrupt, EOFError):
					exit()

		self._clean_menu()

		return self.options[self.index]

	def ask_multiple(
		self,
		esc: bool = True,
	) -> list[str]:
		self.selected_options = []
		with Live(self._group, auto_refresh=False, console=self.console) as live:
			live.update(self._group, refresh=True)
			while True:
				try:
					key = self._get_click()
					if key == "enter":
						break
					elif key == "exit" and esc:
						exit()
					elif key == "down" or key == "up":
						self._update_index(key)
					elif key == "space":
						if self.options[self.index] in self.selected_options:
							self.selected_options.remove(self.options[self.index])
						else:
							self.selected_options.append(self.options[self.index])

					live.update(self._group, refresh=True)
				except (KeyboardInterrupt, EOFError):
					exit()

		self._clean_menu()

		return self.selected_options
