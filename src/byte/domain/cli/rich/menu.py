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
    unselected_color: str = Field(default="text", description="Color for unselected items in multiselect")
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

    def __init__(self, options: tuple[str, ...], start_index: int = 0, window_size: int = 5):
        self.options = options
        self.index = start_index
        self.selected_options: list[str] = []
        self.window_size = window_size
        self.window_start = 0

    def move_up(self) -> None:
        """Move selection up, wrapping to bottom if at top."""
        self.index = (self.index - 1) % len(self.options)
        self._adjust_window()

    def move_down(self) -> None:
        """Move selection down, wrapping to top if at bottom."""
        self.index = (self.index + 1) % len(self.options)
        self._adjust_window()

    def move_left(self) -> None:
        """Move selection left in horizontal menu."""
        self.index = (self.index - 1) % len(self.options)

    def move_right(self) -> None:
        """Move selection right in horizontal menu."""
        self.index = (self.index + 1) % len(self.options)

    def _adjust_window(self) -> None:
        """Adjust the viewing window to keep current selection visible."""
        # If we have fewer options than window size, show all
        if len(self.options) <= self.window_size:
            self.window_start = 0
            return

        # Keep selection in middle of window when possible
        ideal_start = self.index - self.window_size // 2

        # Clamp to valid range
        max_start = len(self.options) - self.window_size
        self.window_start = max(0, min(ideal_start, max_start))

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

    @property
    def visible_options(self) -> tuple[tuple[int, str], ...]:
        """Get the currently visible options with their absolute indices.

        Returns:
                Tuple of (absolute_index, option) pairs for visible options.

        Usage: `for idx, option in state.visible_options: ...`
        """
        if len(self.options) <= self.window_size:
            return tuple(enumerate(self.options))

        end = min(self.window_start + self.window_size, len(self.options))
        return tuple((i, self.options[i]) for i in range(self.window_start, end))

    @property
    def can_scroll_up(self) -> bool:
        """Check if there are more options above the current window."""
        return self.window_start > 0

    @property
    def can_scroll_down(self) -> bool:
        """Check if there are more options below the current window."""
        return len(self.options) > self.window_start + self.window_size


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

    def render_horizontal(self) -> Panel:
        """Render the menu horizontally for confirm dialogs.

        Creates a horizontal layout with options side-by-side,
        using filled/hollow squares to show selection state.

        Usage: `panel = renderer.render_horizontal()` -> display horizontal menu
        """
        from rich.text import Text

        # Build horizontal menu line
        menu_line = Text()

        for idx, option in enumerate(self.state.options):
            if idx > 0:
                # Add spacing between options
                menu_line.append("  /  ", style=self.style.color)

            if idx == self.state.index:
                # Current selection - filled square
                menu_line.append(f"{self.style.selected_char} {option}", style=self.style.selected_color)
            else:
                # Not selected - hollow square
                menu_line.append(f"{self.style.unselected_char} {option}", style=self.style.unselected_color)

        return Panel(
            menu_line,
            title=f"[{self.style.title_color}]{self.title}[/{self.style.title_color}]",
            title_align="left",
            border_style=self.style.border_style,
        )

    def _get_scrollbar_char(self, row_idx: int, visible_count: int) -> str:
        """Get the scrollbar character for a given row.

        Creates a visual scrollbar showing position in the full list.
        Uses █ for the thumb position and │ for the track.

        Args:
                row_idx: Current row index (0 to visible_count-1)
                visible_count: Number of visible rows

        Returns:
                Scrollbar character for this row

        Usage: `char = self._get_scrollbar_char(2, 5)` -> get scrollbar for row 2
        """
        # If all options fit, no scrollbar needed
        if len(self.state.options) <= self.state.window_size:
            return ""

        # Calculate thumb position and size
        total_options = len(self.state.options)

        # Calculate where the thumb should be positioned (0 to visible_count-1)
        # The thumb represents the current window position in the full list
        scroll_ratio = self.state.window_start / (total_options - self.state.window_size)
        thumb_position = int(scroll_ratio * (visible_count - 1))

        # Draw the scrollbar
        if row_idx == thumb_position:
            return f"[{self.style.color}]█[/{self.style.color}]"
        else:
            return f"[{self.style.color}]░[/{self.style.color}]"

    def render(self) -> Panel:
        """Render the menu as a Rich Panel.

        Creates a table grid with current selection, indicators, and options.
        Shows a scrollbar in the fourth column when there are more options than fit.

        Usage: `panel = renderer.render()` -> display menu
        """
        grid = Table.grid(expand=True)
        # First column: selection indicator
        grid.add_column()
        # Second column: selected/unselected character
        grid.add_column()
        # Third column: option text
        grid.add_column(ratio=1)
        # Fourth column: scrollbar
        grid.add_column(justify="right")

        selection_prefix = f"{self.style.selection_char} "
        empty_prefix = "  "

        # Get visible options with their absolute indices
        visible_options = self.state.visible_options
        visible_count = len(visible_options)

        for row_idx, (absolute_idx, option) in enumerate(visible_options):
            # Get scrollbar character for this row
            scrollbar_char = self._get_scrollbar_char(row_idx, visible_count)

            if absolute_idx == self.state.index:
                # Current item - show selection char and highlight
                grid.add_row(
                    f"[{self.style.color}]{selection_prefix}[/{self.style.color}]",
                    f"[{self.style.selected_color}]{self.style.selected_char}  [/{self.style.selected_color}]",
                    f"[{self.style.selected_color}]{option}[/{self.style.selected_color}]",
                    scrollbar_char,
                )
            else:
                # Not current item
                if option in self.state.selected_options:
                    # Selected but not current - filled circle
                    grid.add_row(
                        f"{empty_prefix}",
                        f"[{self.style.selected_color}]{self.style.selected_char}  [/{self.style.selected_color}]",
                        f"[{self.style.selected_color}]{option}[/{self.style.selected_color}]",
                        scrollbar_char,
                    )
                else:
                    # Not selected and not current - hollow circle
                    grid.add_row(
                        f"{empty_prefix}",
                        f"[{self.style.unselected_color}]{self.style.unselected_char}[/{self.style.unselected_color}]",
                        f"[{self.style.unselected_color}]{option}[/{self.style.unselected_color}]",
                        scrollbar_char,
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
        window_size: int = 5,
    ):
        self.state = MenuState(options, start_index, window_size)
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

        Sets border to danger, title to error, and all options to muted color.

        Usage: `self._cancel(live)` -> show cancelled state
        """
        self.style.border_style = "danger"
        self.style.title_color = "error"
        self.style.color = "muted"
        self.style.selected_color = "muted"
        self.style.unselected_color = "muted"
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

    def confirm(self, default: bool = True, esc: bool = True) -> bool | None:
        """Confirmation dialog with Yes/No selection using left/right navigation.

        Navigate with left/right arrow keys or h/l, confirm with Enter,
        cancel with Esc. Uses horizontal layout with filled/hollow squares.

        Args:
                default: Default selection - True for Yes, False for No
                esc: Allow cancellation with Esc key

        Returns:
                True for Yes, False for No, None if cancelled

        Usage: `confirmed = menu.confirm()` -> get yes/no confirmation
        Usage: `confirmed = menu.confirm(default=False)` -> default to No
        """
        # Set up Yes/No options with appropriate default
        self.state.options = ("Yes", "No")
        self.state.index = 0 if default else 1

        with Live(
            self.renderer.render_horizontal(),
            auto_refresh=False,
            console=self.console,
            transient=self.transient,
        ) as live:
            self.live = live
            live.update(self.renderer.render_horizontal(), refresh=True)

            while True:
                try:
                    action = self.input_handler.get_action()

                    if action == "confirm":
                        selected = self.state.index == 0  # True for Yes, False for No
                        self._finalize_confirm(live, selected)
                        return selected

                    if action == "cancel" and esc:
                        self._cancel(live)
                        return None

                    if action in ("left", "right"):
                        self._handle_horizontal_navigation(action, live)

                except (KeyboardInterrupt, EOFError):
                    self._cancel(live)
                    return None

    def _handle_horizontal_navigation(self, action: str, live: Live) -> None:
        """Handle left/right navigation for horizontal menu.

        Usage: `self._handle_horizontal_navigation("left", live)` -> move left
        """
        if action == "left":
            self.state.move_left()
        elif action == "right":
            self.state.move_right()

        live.update(self.renderer.render_horizontal(), refresh=True)

    def _finalize_confirm(self, live: Live, selected: bool) -> None:
        """Finalize confirm dialog after selection.

        Shows only the selected option (Yes or No) with finalized styling.

        Usage: `self._finalize_confirm(live, True)` -> finalize Yes selection
        """
        # Store original state
        original_options = self.state.options
        original_style = self.style

        # Update to finalized state
        self.style = self.style.as_finalized()
        self.renderer.style = self.style

        # Show only selected option
        selected_text = "Yes" if selected else "No"
        self.state.options = (selected_text,)
        self.state.index = 0

        # Update display with horizontal layout
        live.update(self.renderer.render_horizontal(), refresh=True)

        # Restore original state
        self.state.options = original_options
        self.style = original_style
        self.renderer.style = self.style
