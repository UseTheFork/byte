from rich.console import RenderableType
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class ByteLogo(Static):
    """Render the Byte logo with diagonal progress styling."""

    DEFAULT_CSS = """
    ByteLogo {
        width: 100%;
        height: auto;
        overflow-x: hidden;
    }
    """

    def render(self) -> RenderableType:
        """Render the Byte logo with diagonal progress styling and fill remaining width."""
        logo_lines = [
            "░       ░░░  ░░░░  ░░        ░░        ░",
            "▒  ▒▒▒▒  ▒▒▒  ▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒",
            "▓       ▓▓▓▓▓    ▓▓▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓",
            "█  ████  █████  ████████  █████  ███████",
            "█       ██████  ████████  █████        █",
        ]

        styled_logo: list[str] = []
        for row_idx, line in enumerate(logo_lines):
            styled_line = ""
            for col_idx, char in enumerate(line):
                diagonal_progress = (row_idx + col_idx) / (len(logo_lines) + len(line) - 2)
                if diagonal_progress < 0.5:
                    styled_line += f"[$primary]{char}[/$primary]"
                else:
                    styled_line += f"[$secondary]{char}[/$secondary]"

            logo_width = len(line)
            remaining_width = self.size.width - logo_width
            if remaining_width > 0:
                last_char = line[-1] if line else " "
                last_diagonal_progress = (row_idx + len(line) - 1) / (len(logo_lines) + len(line) - 2)
                style = "$primary" if last_diagonal_progress < 0.5 else "$secondary"
                styled_line += f"[{style}]{last_char * remaining_width}[/{style}]"

            styled_logo.append(styled_line)

        return "\n".join(styled_logo)


class Bootbox(Vertical):
    """Container for boot messages with logo."""

    DEFAULT_CSS = """
    Bootbox {
        height: auto;
        width: 100%;
        min-width: 12;
        max-width: 1fr;
        margin: 0 1;
        padding: 0 2;
        border: round $primary;
        overflow-x: hidden;
    }
    """

    def __init__(
        self,
        messages: list[str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.messages = messages

    def compose(self) -> ComposeResult:
        """Compose ByteLogo and messages."""
        yield ByteLogo()
        if self.messages:
            yield Static("\n".join(self.messages))
