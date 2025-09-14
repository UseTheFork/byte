from rich.console import Console
from rich.theme import Theme

from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.ui.config import UIConfig


class UIServiceProvider(ServiceProvider):
    """Service provider for UI system."""

    async def register(self, container: Container) -> None:
        """Register UI services in the container."""

        # Register UI config schema first
        config_service = await container.make(abstract="config")
        config_service.register_schema("ui", UIConfig)

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
            },
            False,
        )

        console = Console(theme=catppuccin_mocha_theme)
        console.print("░       ░░░  ░░░░  ░░        ░░        ░", style="primary")
        console.print("▒  ▒▒▒▒  ▒▒▒  ▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒", style="primary")
        console.print("▓       ▓▓▓▓▓    ▓▓▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓", style="primary")
        console.print("█  ████  █████  ████████  █████  ███████", style="primary")
        console.print("█       ██████  ████████  █████        █", style="primary")
        console.print("┌── The No Vibe CLI Agent", style="text")

        container.singleton("console", lambda: console)

    async def boot(self, container: Container):
        """Boot UI services."""
        # UI services are ready to use after registration
        pass

    def provides(self) -> list:
        return ["console"]
