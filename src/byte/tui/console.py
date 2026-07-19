from typing import TYPE_CHECKING, Literal

from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.theme import Theme

from byte.tui.rich.menu import Menu
from byte.tui.themes.cli_theme_regisrty import CliThemeRegistry

if TYPE_CHECKING:
    from byte.foundation import Application


class Console:
    """Manage terminal output with themed styling."""

    def __init__(self, app: Application, **kwargs):
        """Initialize the console with configured theme."""
        self.app = app
        self.ui_theme = "byte-catppuccin-mocha"
        self.syntax_theme = "monokai"
        self.setup_console()

    def setup_console(self):
        # Load the selected Catppuccin theme variant.
        theme_registry = CliThemeRegistry()
        selected_theme = theme_registry.get_theme(self.ui_theme)

        # Apply Base16 colors to semantic style names.
        byte_theme = Theme(
            {
                "text": selected_theme.base05,  # Default Foreground
                "success": selected_theme.base0B,  # Green - Strings, Inserted
                "error": selected_theme.base08,  # Red - Variables, Tags
                "warning": selected_theme.base0A,  # Yellow - Classes, Bold
                "info": selected_theme.base0C,  # Teal - Support, Regex
                "danger": selected_theme.base08,  # Red - Variables, Tags
                "primary": selected_theme.base0D,  # Blue - Functions, Headings
                "secondary": selected_theme.base0E,  # Mauve - Keywords, Italic
                "muted": selected_theme.base03,  # Comments, Invisibles
                "subtle": selected_theme.base04,  # Dark Foreground
                "active_border": selected_theme.base07,  # Light Background
                "inactive_border": selected_theme.base03,  # Comments, Invisibles
            }
        )
        self._console = RichConsole(theme=byte_theme)

    @property
    def console(self) -> RichConsole:
        """Access the underlying Rich Console instance for advanced operations."""
        return self._console

    @property
    def width(self) -> int:
        """Get the current console width in characters."""
        return self.console.width

    @property
    def height(self) -> int:
        """Get the current console height in lines."""
        return self.console.height

    def print_boot_status(
        self, status: Literal["ok", "fail", "warn"], message: str, subject: str | None = None, **kwargs
    ) -> None:
        """Print a boot status message in Linux-style format."""
        valid_statuses = {"ok", "fail", "warn"}
        if status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}, got '{status}'")

        message_map = {
            "ok": " OK ",
            "fail": "FAIL",
            "warn": "WARN",
        }
        style_map = {
            "ok": "success",
            "fail": "error",
            "warn": "warning",
        }
        display_status = message_map[status]
        style = style_map[status]

        if subject is not None:
            output = f"[  [{style}]{display_status}[/{style}]  ] [muted]{message}[/muted] [text]{subject}[/text]"
        else:
            output = f"[  [{style}]{display_status}[/{style}]  ] {message}"
        self.console.print(output, **kwargs)

    def print_success(self, message: str, **kwargs) -> None:
        """Print a success message."""
        self.console.print(f"[success]{message}[/success]", **kwargs)

    def print_warning(self, message: str, **kwargs) -> None:
        """Print a warning message."""
        self.console.print(f"[warning]{message}[/warning]", **kwargs)

    def print_error(self, message: str, **kwargs) -> None:
        """Print an error message."""
        self.console.print(f"[error]{message}[/error]", **kwargs)

    def print_info(self, message: str, **kwargs) -> None:
        """Print an informational message."""
        self.console.print(f"[info]{message}[/info]", **kwargs)

    def print(self, *args, **kwargs) -> None:
        """Print to console with Rich formatting support."""
        self.console.print(*args, **kwargs)

    def syntax(self, *args, **kwargs):
        """Create a themed Syntax component for code display."""
        kwargs.setdefault("theme", self.syntax_theme)
        return Syntax(*args, **kwargs)

    def print_error_panel(self, *args, **kwargs):
        """Print a panel with error styling."""
        kwargs.setdefault("border_style", "error")
        self.console.print(self.panel(*args, **kwargs))

    def print_warning_panel(self, *args, **kwargs):
        """Print a panel with warning styling."""
        kwargs.setdefault("border_style", "warning")
        self.console.print(self.panel(*args, **kwargs))

    def print_success_panel(self, *args, **kwargs):
        """Print a panel with success styling."""
        kwargs.setdefault("border_style", "success")
        self.console.print(self.panel(*args, **kwargs))

    def print_info_panel(self, *args, **kwargs):
        """Print a panel with info styling."""
        kwargs.setdefault("border_style", "info")
        self.console.print(self.panel(*args, **kwargs))

    def print_panel(self, *args, **kwargs):
        """Print a themed panel to the console."""
        self.console.print(self.panel(*args, **kwargs))

    def panel(self, *args, **kwargs):
        """Create a themed Panel component."""
        kwargs.setdefault("title_align", "left")
        kwargs.setdefault("subtitle_align", "left")
        kwargs.setdefault("border_style", "inactive_border")
        return Panel(*args, **kwargs)

    def rule(self, *args, **kwargs):
        """Create a horizontal rule separator."""
        kwargs.setdefault("style", "text")
        kwargs.setdefault("characters", "─")
        kwargs.setdefault("align", "left")
        self.console.print(Rule(*args, **kwargs))

    def select(self, *args, **kwargs):
        """Display a single-selection menu and return the chosen option."""
        kwargs.setdefault("console", self.console)
        menu = Menu(*args, **kwargs)
        return menu.select()

    def multiselect(self, *args, **kwargs):
        """Display a multi-selection menu and return the chosen options."""
        kwargs.setdefault("console", self.console)
        menu = Menu(*args, **kwargs)
        return menu.multiselect()

    def confirm(self, message: str = "Confirm?", default: bool = True, **kwargs) -> bool | None:
        """Display a confirmation dialog with Yes/No options."""
        kwargs.setdefault("console", self.console)
        kwargs.setdefault("title", message)
        menu = Menu("Yes", "No", **kwargs)
        return menu.confirm(default=default)

    def __getattr__(self, name: str):
        """Proxy unknown method calls to the underlying Rich Console."""
        return getattr(self.console, name)
