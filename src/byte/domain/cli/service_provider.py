from rich.console import Console
from rich.rule import Rule
from rich.theme import Theme

from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.interactions_service import InteractionService
from byte.domain.cli.service.prompt_toolkit_service import PromptToolkitService
from byte.domain.cli.service.stream_rendering_service import (
    StreamRenderingService,
)


class CLIServiceProvider(ServiceProvider):
    """Service provider for UI system."""

    def services(self):
        return [StreamRenderingService, InteractionService, PromptToolkitService]

    async def boot(self, container: Container):
        """Boot UI services."""

        # "pink": "#f5c2e7",
        # "mauve": "#cba6f7",
        # "red": "#f38ba8",
        # "maroon": "#eba0ac",
        # "peach": "#fab387",
        # "yellow": "#f9e2af",
        # "green": "#a6e3a1",
        # "teal": "#94e2d5",
        # "sky": "#89dceb",
        # "sapphire": "#74c7ec",
        # "blue": "#89b4fa",
        # "lavender": "#b4befe",
        # "text": "#cdd6f4",
        # "subtext1": "#bac2de",
        # "subtext0": "#a6adc8",
        # "overlay2": "#9399b2",
        # "overlay1": "#7f849c",
        # "overlay0": "#6c7086",
        # "surface2": "#585b70",
        # "surface1": "#45475a",
        # "surface0": "#313244",
        # "base": "#1e1e2e",
        # "mantle": "#181825",
        # "crust": "#11111b",

        catppuccin_mocha_theme = Theme(
            {
                "text": "#cdd6f4",
                "success": "#a6e3a1",
                "error": "#f38ba8",
                "warning": "#f9e2af",
                "info": "#94e2d5",
                "danger": "#f38ba8",
                "primary": "#89b4fa",
                "secondary": "#cba6f7",
                "muted": "#6c7086",
                "subtle": "#a6adc8",
                "lavender": "#b4befe",
            }
        )

        console = await container.make(Console)
        console.push_theme(catppuccin_mocha_theme)

        # Create diagonal gradient from primary to secondary color
        # AI: How can we use `console.width` to get the remaning width of the line and at the end of each line print the last charetcor to fill the space ai?
        logo_lines = [
            "░       ░░░  ░░░░  ░░        ░░        ░",
            "▒  ▒▒▒▒  ▒▒▒  ▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒",
            "▓       ▓▓▓▓▓    ▓▓▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓",
            "█  ████  █████  ████████  █████  ███████",
            "█       ██████  ████████  █████        █",
        ]

        for row_idx, line in enumerate(logo_lines):
            styled_line = ""
            for col_idx, char in enumerate(line):
                # Calculate diagonal position (0.0 = top-left, 1.0 = bottom-right)
                diagonal_progress = (row_idx + col_idx) / (
                    len(logo_lines) + len(line) - 2
                )

                # Use primary for first half, secondary for second half of diagonal
                if diagonal_progress < 0.5:
                    styled_line += f"[primary]{char}[/primary]"
                else:
                    styled_line += f"[secondary]{char}[/secondary]"

            # Calculate remaining width and fill with the last character
            logo_width = len(
                line
            )  # Actual character count (Rich styles don't add to width)
            remaining_width = console.width - logo_width

            if remaining_width > 0:
                # Use the last character to fill the remaining space
                last_char = line[-1] if line else " "
                # Apply the same style as the last character would have
                last_diagonal_progress = (row_idx + len(line) - 1) / (
                    len(logo_lines) + len(line) - 2
                )
                style = "primary" if last_diagonal_progress < 0.5 else "secondary"
                styled_line += f"[{style}]{last_char * remaining_width}[/{style}]"

            console.print(styled_line)

        console.print()

        console.print(
            Rule(
                "╭─ Booting",
                style="text",
                align="left",
                characters="─",
            )
        )
        console.print("│ ", style="text")
