from typing import Optional

import click
from pydantic import BaseModel, Field
from rich import get_console
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


class MenuStyle(BaseModel):
	"""Menu visual styling configuration."""

	color: str = Field(default="secondary", description="Color for non-selected items")
	selected_color: str = Field(default="primary", description="Color for selected/highlighted items")
	title_color: str = Field(default="text", description="Color for panel title")
	border_style: str = Field(default="active_border", description="Border style for the menu panel")
	selection_char: str = Field(default="›", description="Character shown next to current item")  # noqa: RUF001
	selected_char: str = Field(default="◼", description="Character for selected items in multiselect")
	unselected_char: str = Field(default="◻", description="Character for unselected items in multiselect")

	def as_finalized(self) -> "MenuStyle":
		"""Return a new style configured for finalized state.

		Creates a copy with muted colors and no indicator characters.

		Usage: `finalized_style = style.as_finalized()`
		"""
		return MenuStyle(
			color=self.color,
			selected_color=self.selected_color,
			title_color="muted",
			border_style="inactive_border",
			selection_char="",
			selected_char="",
			unselected_char="",
		)


class MenuState:
	"""Manages menu selection state and navigation logic."""

	def __init__(self, options: tuple[str, ...], start_index: int = 0):
		self.options = options
		self.index = start_index
		self.selected_options: list[str] = []

	def move_up(self) -> None:
		"""Move selection up, wrapping to bottom if at top."""
		self.index = (self.index - 1) % len(self.options)

	def move_down(self) -> None:
		"""Move selection down, wrapping to top if at bottom."""
		self.index = (self.index + 1) % len(self.options)

	def toggle_selection(self) -> None:
		"""Toggle selection of current option in multiselect mode."""
		option = self.options[self.index]
		if option in self.selected_options:
			self.selected_options.remove(option)
		else:
			self.selected_options.append(option)

	@property
	def current_option(self) -> str:
		"""Get the currently highlighted option."""
		return self.options[self.index]


class MenuInputHandler:
	"""Handles keyboard input for menu navigation."""

	@staticmethod
	def get_action() -> str | None:
		"""Map keyboard input to menu actions.

		Returns action name or None if input not recognized.

		Usage: `action = handler.get_action()` -> "confirm", "up", "down", etc.
		"""
		match click.getchar():
			case "\r":
				return "confirm"
			case "\x1b[B" | "s" | "S" | "àP" | "j":
				return "down"
			case "\x1b[A" | "w" | "W" | "àH" | "k":
				return "up"
			case "\x1b[D" | "a" | "A" | "àK" | "h":
				return "left"
			case "\x1b[C" | "d" | "D" | "àM" | "l":
				return "right"
			case " " | "\x0d":
				return "toggle"
			case "\x1b":
				return "cancel"
			case _:
				return None


class MenuRenderer:
	"""Handles menu visual presentation."""

	def __init__(self, state: MenuState, style: MenuStyle, title: str):
		self.state = state
		self.style = style
		self.title = title

	def render(self) -> Panel:
		"""Render the menu as a Rich Panel.

		Creates a table grid with current selection, indicators, and options.

		Usage: `panel = renderer.render()` -> display menu
		"""
		grid = Table.grid(expand=True)
		# First column: selection indicator
		grid.add_column()
		# Second column: selected/unselected character
		grid.add_column()
		# Third column: option text
		grid.add_column(ratio=1)
		# Fourth column: empty for scrolling
		grid.add_column(justify="right")

		selection_prefix = f"{self.style.selection_char} "
		empty_prefix = "  "

		for idx, option in enumerate(self.state.options):
			if idx == self.state.index:
				# Current item - show selection char and highlight
				grid.add_row(
					f"[{self.style.color}]{selection_prefix}[/{self.style.color}]",
					f"[{self.style.selected_color}]{self.style.selected_char}  [/{self.style.selected_color}]",
					f"[{self.style.selected_color}]{option}[/{self.style.selected_color}]",
					"",
				)
			else:
				# Not current item
				if option in self.state.selected_options:
					# Selected but not current - filled circle
					grid.add_row(
						f"{empty_prefix}",
						f"[{self.style.selected_color}]{self.style.selected_char}  [/{self.style.selected_color}]",
						f"[{self.style.selected_color}]{option}[/{self.style.selected_color}]",
						"",
					)
				else:
					# Not selected and not current - hollow circle
					grid.add_row(
						f"{empty_prefix}",
						f"{self.style.unselected_char}",
						f"{option}",
						"",
					)

		return Panel(
			grid,
			title=f"[{self.style.title_color}]{self.title}[/{self.style.title_color}]",
			title_align="left",
			border_style=self.style.border_style,
		)


# Credits to https://github.com/gbPagano/rich_menu/blob/main/rich_menu/menu.py
class Menu:
	"""User-friendly menu for selection in terminal.

	Provides interactive single and multi-select menus with keyboard navigation.
	"""

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
		self.state = MenuState(options, start_index)
		self.style = MenuStyle(
			color=color,
			selected_color=selected_color,
		)
		self.renderer = MenuRenderer(self.state, self.style, title)
		self.input_handler = MenuInputHandler()

		self.title = title
		self.transient = transient
		self.console = console if console is not None else get_console()
		self.live: Optional[Live] = None

	def _create_live_display(self) -> Live:
		"""Create a Live display context for the menu.

		Usage: `with self._create_live_display() as live: ...`
		"""
		return Live(
			self.renderer.render(),
			auto_refresh=False,
			console=self.console,
			transient=self.transient,
		)

	def _update_display(self, live: Live) -> None:
		"""Update the live display with current menu state.

		Usage: `self._update_display(live)` -> refresh display
		"""
		live.update(self.renderer.render(), refresh=True)

	def _handle_navigation(self, action: str, live: Live) -> None:
		"""Handle up/down navigation actions.

		Usage: `self._handle_navigation("up", live)` -> move selection up
		"""
		if action == "up":
			self.state.move_up()
		elif action == "down":
			self.state.move_down()
		self._update_display(live)

	def _cancel(self, live: Live) -> None:
		"""Handle menu cancellation with danger styling.

		Usage: `self._cancel(live)` -> show cancelled state
		"""
		self.style.border_style = "danger"
		self.renderer.style = self.style
		self._update_display(live)

	def _finalize(self, live: Live, selected: str | list[str]) -> None:
		"""Finalize menu display after selection.

		Updates style to finalized state, shows only selected options,
		then restores original state for reusability.

		Usage: `self._finalize(live, selected_option)` -> show final state
		"""
		# Store original state
		original_options = self.state.options
		original_style = self.style

		# Update to finalized state
		self.style = self.style.as_finalized()
		self.renderer.style = self.style

		# Show only selected options
		if isinstance(selected, list):
			self.state.options = tuple(selected)
		else:
			self.state.options = (selected,)

		# Update display
		self._update_display(live)

		# Restore original state for reusability
		self.state.options = original_options
		self.style = original_style
		self.renderer.style = self.style

	def select(self, esc: bool = True) -> str | None:
		"""Single selection mode.

		Navigate with arrow keys or hjkl/wasd, confirm with Enter, cancel with Esc.

		Args:
			esc: Allow cancellation with Esc key

		Returns:
			Selected option or None if cancelled

		Usage: `choice = menu.select()` -> get user's selection
		"""
		with self._create_live_display() as live:
			self.live = live
			self._update_display(live)

			while True:
				try:
					action = self.input_handler.get_action()

					if action == "confirm":
						selected = self.state.current_option
						self._finalize(live, selected)
						return selected

					if action == "cancel" and esc:
						self._cancel(live)
						return None

					if action in ("up", "down"):
						self._handle_navigation(action, live)

				except (KeyboardInterrupt, EOFError):
					self._cancel(live)
					return None

	def multiselect(self, esc: bool = True) -> list[str] | None:
		"""Multiple selection mode.

		Navigate with arrow keys or hjkl/wasd, toggle with Space,
		confirm with Enter, cancel with Esc.

		Args:
			esc: Allow cancellation with Esc key

		Returns:
			List of selected options or None if cancelled

		Usage: `choices = menu.multiselect()` -> get multiple selections
		"""
		self.state.selected_options = []

		with self._create_live_display() as live:
			self.live = live
			self._update_display(live)

			while True:
				try:
					action = self.input_handler.get_action()

					if action == "confirm":
						self._finalize(live, self.state.selected_options)
						return self.state.selected_options

					if action == "cancel" and esc:
						self._cancel(live)
						return None

					if action == "toggle":
						self.state.toggle_selection()
						self._update_display(live)

					if action in ("up", "down"):
						self._handle_navigation(action, live)

				except (KeyboardInterrupt, EOFError):
					self._cancel(live)
					return None
