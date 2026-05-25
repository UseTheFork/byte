from typing import TYPE_CHECKING

from textual.theme import Theme

from byte.tui.themes.base_theme_registry import BaseThemeRegistry

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class TuiThemeRegistry(BaseThemeRegistry):
    """Registry for managing and registering Catppuccin themes with Textual."""

    def register_themes(self, tui: ByteTUI):
        # .venv/lib/python3.14/site-packages/textual/design.py
        for theme_name, byte_theme in self.themes.items():
            is_dark = theme_name != "byte-catppuccin-latte"

            textual_theme = Theme(
                name=theme_name,
                primary=byte_theme.base0D,
                secondary=byte_theme.base0E,
                accent=byte_theme.base09,
                foreground=byte_theme.base05,
                background=byte_theme.base00,
                success=byte_theme.base0B,
                warning=byte_theme.base0A,
                error=byte_theme.base08,
                surface=byte_theme.base01,
                panel=byte_theme.base02,
                dark=is_dark,
                variables={
                    "block-cursor-text-style": "none",
                    "footer-key-foreground": byte_theme.base0D,
                    "input-selection-background": f"{byte_theme.base0D} 35%",
                },
            )
            tui.register_theme(textual_theme)
