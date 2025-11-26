from typing import Literal, Optional

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class ByteTheme:
    """Base16 color theme for terminal styling.

    Base16 Color Usage Guide:
    - base00: Default Background
    - base01: Lighter Background (status bars, line numbers, folding marks)
    - base02: Selection Background
    - base03: Comments, Invisibles, Line Highlighting
    - base04: Dark Foreground (status bars)
    - base05: Default Foreground, Caret, Delimiters, Operators
    - base06: Light Foreground (rarely used)
    - base07: Light Background (rarely used)
    - base08: Variables, XML Tags, Markup Link Text, Markup Lists, Diff Deleted
    - base09: Integers, Boolean, Constants, XML Attributes, Markup Link Url
    - base0A: Classes, Markup Bold, Search Text Background
    - base0B: Strings, Inherited Class, Markup Code, Diff Inserted
    - base0C: Support, Regular Expressions, Escape Characters, Markup Quotes
    - base0D: Functions, Methods, Attribute IDs, Headings
    - base0E: Keywords, Storage, Selector, Markup Italic, Diff Changed
    - base0F: Deprecated, Opening/Closing Embedded Language Tags
    """

    base00: str
    base01: str
    base02: str
    base03: str
    base04: str
    base05: str
    base06: str
    base07: str
    base08: str
    base09: str
    base0A: str
    base0B: str
    base0C: str
    base0D: str
    base0E: str
    base0F: str


# Catppuccin Mocha theme based on Base16 specification.
CATPPUCCIN_MOCHA = ByteTheme(
    base00="#1e1e2e",  # base - Default Background
    base01="#181825",  # mantle - Lighter Background
    base02="#313244",  # surface0 - Selection Background
    base03="#45475a",  # surface1 - Comments, Invisibles
    base04="#585b70",  # surface2 - Dark Foreground
    base05="#cdd6f4",  # text - Default Foreground
    base06="#f5e0dc",  # rosewater - Light Foreground
    base07="#b4befe",  # lavender - Light Background
    base08="#f38ba8",  # red - Variables, Tags
    base09="#fab387",  # peach - Integers, Constants
    base0A="#f9e2af",  # yellow - Classes, Bold
    base0B="#a6e3a1",  # green - Strings, Inserted
    base0C="#94e2d5",  # teal - Support, Regex
    base0D="#89b4fa",  # blue - Functions, Headings
    base0E="#cba6f7",  # mauve - Keywords, Italic
    base0F="#f2cdcd",  # flamingo - Deprecated
)

# Catppuccin Macchiato theme based on Base16 specification.
CATPPUCCIN_MACCHIATO = ByteTheme(
    base00="#24273a",  # base - Default Background
    base01="#1e2030",  # mantle - Lighter Background
    base02="#363a4f",  # surface0 - Selection Background
    base03="#494d64",  # surface1 - Comments, Invisibles
    base04="#5b6078",  # surface2 - Dark Foreground
    base05="#cad3f5",  # text - Default Foreground
    base06="#f4dbd6",  # rosewater - Light Foreground
    base07="#b7bdf8",  # lavender - Light Background
    base08="#ed8796",  # red - Variables, Tags
    base09="#f5a97f",  # peach - Integers, Constants
    base0A="#eed49f",  # yellow - Classes, Bold
    base0B="#a6da95",  # green - Strings, Inserted
    base0C="#8bd5ca",  # teal - Support, Regex
    base0D="#8aadf4",  # blue - Functions, Headings
    base0E="#c6a0f6",  # mauve - Keywords, Italic
    base0F="#f0c6c6",  # flamingo - Deprecated
)


# Catppuccin Latte theme based on Base16 specification.
CATPPUCCIN_LATTE = ByteTheme(
    base00="#eff1f5",  # base - Default Background
    base01="#e6e9ef",  # mantle - Lighter Background
    base02="#ccd0da",  # surface0 - Selection Background
    base03="#bcc0cc",  # surface1 - Comments, Invisibles
    base04="#acb0be",  # surface2 - Dark Foreground
    base05="#4c4f69",  # text - Default Foreground
    base06="#dc8a78",  # rosewater - Light Foreground
    base07="#7287fd",  # lavender - Light Background
    base08="#d20f39",  # red - Variables, Tags
    base09="#fe640b",  # peach - Integers, Constants
    base0A="#df8e1d",  # yellow - Classes, Bold
    base0B="#40a02b",  # green - Strings, Inserted
    base0C="#179299",  # teal - Support, Regex
    base0D="#1e66f5",  # blue - Functions, Headings
    base0E="#8839ef",  # mauve - Keywords, Italic
    base0F="#dd7878",  # flamingo - Deprecated
)


# Catppuccin Frappe theme based on Base16 specification.
CATPPUCCIN_FRAPPE = ByteTheme(
    base00="#303446",  # base - Default Background
    base01="#292c3c",  # mantle - Lighter Background
    base02="#414559",  # surface0 - Selection Background
    base03="#51576d",  # surface1 - Comments, Invisibles
    base04="#626880",  # surface2 - Dark Foreground
    base05="#c6d0f5",  # text - Default Foreground
    base06="#f2d5cf",  # rosewater - Light Foreground
    base07="#babbf1",  # lavender - Light Background
    base08="#e78284",  # red - Variables, Tags
    base09="#ef9f76",  # peach - Integers, Constants
    base0A="#e5c890",  # yellow - Classes, Bold
    base0B="#a6d189",  # green - Strings, Inserted
    base0C="#81c8be",  # teal - Support, Regex
    base0D="#8caaee",  # blue - Functions, Headings
    base0E="#ca9ee6",  # mauve - Keywords, Italic
    base0F="#eebebe",  # flamingo - Deprecated
)


@dataclass(frozen=True)
class ThemeRegistry:
    """Registry mapping theme variant names to ByteTheme instances.

    Provides type-safe access to Catppuccin theme variants with descriptive
    metadata about each theme's characteristics.

    Usage: `theme = ThemeRegistry().get_theme("mocha")`
    """

    mocha: ByteTheme = CATPPUCCIN_MOCHA
    macchiato: ByteTheme = CATPPUCCIN_MACCHIATO
    latte: ByteTheme = CATPPUCCIN_LATTE
    frappe: ByteTheme = CATPPUCCIN_FRAPPE

    def get_theme(self, variant: Literal["mocha", "macchiato", "latte", "frappe"]) -> ByteTheme:
        """Get a theme by variant name.

        Usage: `theme = registry.get_theme("mocha")`

        Args:
                variant: Theme variant name (mocha, macchiato, latte, or frappe)

        Returns:
                ByteTheme: The requested Catppuccin theme instance
        """
        return getattr(self, variant)


@dataclass(frozen=True)
class SubprocessResult:
    """Result of a subprocess execution.

    Contains the exit code, stdout, and stderr from running a subprocess command.

    Usage: `result = SubprocessResult(exit_code=0, stdout="output", stderr="")`
    """

    exit_code: int
    stdout: str
    stderr: str
    command: str
    cwd: Optional[str] = None
