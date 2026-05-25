from typing import TYPE_CHECKING

from byte.tui.themes.base_theme_registry import BaseThemeRegistry

if TYPE_CHECKING:
    pass


class CliThemeRegistry(BaseThemeRegistry):
    """Registry for managing and registering themes with Rich CLI."""

    def get_theme(self, theme_name: str = "byte-catppuccin-mocha"):
        selected_theme = self.themes[theme_name]
        return selected_theme
