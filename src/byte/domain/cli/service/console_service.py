from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.theme import Theme

from byte.core.service.base_service import Service
from byte.domain.cli.rich.menu import Menu
from byte.domain.cli.rich.panel_rule import PanelBottom, PanelTop
from byte.domain.cli.schemas import ByteTheme, ThemeRegistry


class ConsoleService(Service):
    """Console service for terminal output with themed styling."""

    _console: Console

    async def boot(self, **kwargs) -> None:
        """Initialize the console with configured theme.

        Loads the Catppuccin theme variant specified in config and applies
        Base16 colors to semantic style names for consistent terminal output.

        Usage: Called automatically during service initialization
        """

        # Load the selected Catppuccin theme variant.
        theme_registry = ThemeRegistry()
        selected_theme: ByteTheme = theme_registry.get_theme(self._config.cli.ui_theme)

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
        self._console = Console(theme=byte_theme)

    @property
    def console(self) -> Console:
        """Access the underlying Rich Console instance for advanced operations.

        Most operations should use the service's wrapper methods (print, panel, etc.),
        but direct console access is available for advanced features not wrapped by
        the service API.

        Usage: `service.console.clear()`
        Usage: `service.console.set_window_title("ByteSmith")`
        """
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

    def print_success(self, message: str, **kwargs) -> None:
        """Print a success message with success styling.

        Wraps the message in [success] tags for consistent success display across
        the application using the theme's configured success color.

        Usage:
                `service.print_success("Operation completed successfully")`
                `service.print_success("File saved", highlight=False)`

        Args:
                message: Success message to display
                **kwargs: Additional keyword arguments passed to Console.print()
        """
        self._console.print(f"[success]{message}[/success]", **kwargs)

    def print_warning(self, message: str, **kwargs) -> None:
        """Print a warning message with warning styling.

        Wraps the message in [warning] tags for consistent warning display across
        the application using the theme's configured warning color.

        Usage:
                `service.print_warning("Operation may take a while")`
                `service.print_warning("Deprecated feature used", highlight=False)`

        Args:
                message: Warning message to display
                **kwargs: Additional keyword arguments passed to Console.print()
        """
        self._console.print(f"[warning]{message}[/warning]", **kwargs)

    def print_error(self, message: str, **kwargs) -> None:
        """Print an error message with error styling.

        Wraps the message in [error] tags for consistent error display across
        the application using the theme's configured error color.

        Usage:
                `service.print_error("File not found")`
                `service.print_error("Operation failed", highlight=False)`

        Args:
                message: Error message to display
                **kwargs: Additional keyword arguments passed to Console.print()
        """
        self._console.print(f"[error]{message}[/error]", **kwargs)

    def print_info(self, message: str, **kwargs) -> None:
        """Print an informational message with info styling.

        Wraps the message in [info] tags for consistent info display across
        the application using the theme's configured info color.

        Usage:
                `service.print_info("Processing file...")`
                `service.print_info("Loading configuration", highlight=False)`

        Args:
                message: Informational message to display
                **kwargs: Additional keyword arguments passed to Console.print()
        """
        self._console.print(f"[info]{message}[/info]", **kwargs)

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

    def print_error_panel(self, *args, **kwargs):
        """Print a panel with error styling to the console.

        Creates and prints a panel with error border styling for displaying
        error messages in a visually distinct way.

        Usage:
                `service.print_error_panel("Error occurred", title="Error")`
                `service.print_error_panel(error_text, subtitle="Details")`

        Args:
                *args: Positional arguments passed to panel()
                **kwargs: Keyword arguments passed to panel(), with error border style default
        """
        kwargs.setdefault("border_style", "error")
        self.console.print(self.panel(*args, **kwargs))

    def print_warning_panel(self, *args, **kwargs):
        """Print a panel with warning styling to the console.

        Creates and prints a panel with warning border styling for displaying
        warning messages in a visually distinct way.

        Usage:
                `service.print_warning_panel("Warning message", title="Warning")`
                `service.print_warning_panel(warning_text, subtitle="Details")`

        Args:
                *args: Positional arguments passed to panel()
                **kwargs: Keyword arguments passed to panel(), with warning border style default
        """
        kwargs.setdefault("border_style", "warning")
        self.console.print(self.panel(*args, **kwargs))

    def print_success_panel(self, *args, **kwargs):
        """Print a panel with success styling to the console.

        Creates and prints a panel with success border styling for displaying
        success messages in a visually distinct way.

        Usage:
                `service.print_success_panel("Operation completed", title="Success")`
                `service.print_success_panel(success_text, subtitle="Details")`

        Args:
                *args: Positional arguments passed to panel()
                **kwargs: Keyword arguments passed to panel(), with success border style default
        """
        kwargs.setdefault("border_style", "success")
        self.console.print(self.panel(*args, **kwargs))

    def print_panel(self, *args, **kwargs):
        """Print a themed panel to the console with default styling.

        Creates and immediately prints a panel with left-aligned title/subtitle
        and inactive border styling. Proxies to panel() then console.print().

        Usage:
                `service.print_panel("Content", title="Section")`
                `service.print_panel(rich_object, subtitle="Details")`

        Args:
                *args: Positional arguments passed to panel()
                **kwargs: Keyword arguments passed to panel()
        """
        self.console.print(self.panel(*args, **kwargs))

    def panel(self, *args, **kwargs):
        """Create a themed Panel component with default styling.

        Configures panel with left-aligned title/subtitle and inactive border
        style. Returns the panel for further customization or delayed rendering.

        Usage:
                `panel = service.panel("Content", title="Header")`
                `panel = service.panel(syntax, border_style="primary")`

        Args:
                *args: Positional arguments passed to Rich's Panel constructor
                **kwargs: Keyword arguments passed to Panel, with defaults applied

        Returns:
                Panel: Configured Rich Panel component ready for rendering
        """
        kwargs.setdefault("title_align", "left")
        kwargs.setdefault("subtitle_align", "left")
        kwargs.setdefault("border_style", "inactive_border")
        return Panel(*args, **kwargs)

    def rule(self, *args, **kwargs):
        """Print a horizontal rule with default styling.

        Creates and prints a left-aligned horizontal line separator using
        the configured text style and box-drawing characters.

        Usage:
                `service.rule("Section Title")`
                `service.rule("Step 2", style="primary")`

        Args:
                *args: Positional arguments passed to Rich's Rule constructor
                **kwargs: Keyword arguments passed to Rule, with defaults applied
        """
        kwargs.setdefault("style", "text")
        kwargs.setdefault("characters", "─")
        kwargs.setdefault("align", "left")
        self.console.print(Rule(*args, **kwargs))

    def panel_top(self, *args, **kwargs):
        """Print the top border of a panel with optional title.

        Creates and prints a panel top border with left-aligned title
        and inactive border styling by default.

        Usage:
                `service.panel_top("Section Title")`
                `service.panel_top("Header", border_style="primary")`

        Args:
                *args: Positional arguments passed to PanelTop constructor
                **kwargs: Keyword arguments passed to PanelTop, with defaults applied
        """
        kwargs.setdefault("border_style", "inactive_border")
        kwargs.setdefault("align", "left")
        self.console.print(PanelTop(*args, **kwargs))

    def panel_bottom(self, *args, **kwargs):
        """Print the bottom border of a panel with optional subtitle.

        Creates and prints a panel bottom border with left-aligned subtitle
        and inactive border styling by default.

        Usage:
                `service.panel_bottom("End of Section")`
                `service.panel_bottom("Footer", border_style="primary")`

        Args:
                *args: Positional arguments passed to PanelBottom constructor
                **kwargs: Keyword arguments passed to PanelBottom, with defaults applied
        """
        kwargs.setdefault("border_style", "inactive_border")
        kwargs.setdefault("align", "left")
        self.console.print(PanelBottom(*args, **kwargs))

    def select(self, *args, **kwargs):
        """Show a single-selection menu and return the chosen option.

        Creates a Menu component with the configured console and allows the user
        to select one option from the provided choices using keyboard navigation.

        Args:
                *args: Positional arguments passed to Menu constructor (typically choices)
                **kwargs: Keyword arguments passed to Menu, with console defaulted

        Returns:
                The selected option value

        Usage:
                `choice = service.select("Option 1", "Option 2", "Option 3")`
                `choice = service.select(*options, title="Choose one")`
        """
        kwargs.setdefault("console", self._console)
        menu = Menu(*args, **kwargs)
        return menu.select()

    def multiselect(self, *args, **kwargs):
        """Show a multi-selection menu and return the chosen options.

        Creates a Menu component with the configured console and allows the user
        to select multiple options from the provided choices using keyboard navigation.

        Args:
                *args: Positional arguments passed to Menu constructor (typically choices)
                **kwargs: Keyword arguments passed to Menu, with console defaulted

        Returns:
                List of selected option values

        Usage:
                `choices = service.multiselect("Option 1", "Option 2", "Option 3")`
                `choices = service.multiselect(*options, title="Choose multiple")`
        """
        kwargs.setdefault("console", self._console)
        menu = Menu(*args, **kwargs)
        return menu.multiselect()

    def confirm(self, message: str = "Confirm?", default: bool = True, **kwargs) -> bool | None:
        """Show a confirmation dialog with Yes/No options.

        Navigate with left/right arrow keys, confirm with Enter, cancel with Esc.

        Args:
                message: Confirmation question to display
                default: Default selection - True for Yes, False for No
                **kwargs: Additional arguments passed to Menu

        Returns:
                True for Yes, False for No, None if cancelled

        Usage:
                `if console.confirm("Continue?"): ...`
                `if console.confirm("Delete file?", default=False): ...`
        """
        kwargs.setdefault("console", self._console)
        kwargs.setdefault("title", message)
        menu = Menu("Yes", "No", **kwargs)
        return menu.confirm(default=default)
