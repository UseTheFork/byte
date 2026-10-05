"""Generate tui.tcss utility styles.

This script generates utility CSS classes for the Textual TUI framework,
including margin, padding, text alignment, height, and width utilities.

Usage: `uv run python src/scripts/generate_tui_styles.py`
"""

# Credits to https://github.com/koaning/tuilwindcss/blob/main/tuilwindcss/construct.py

from pathlib import Path

COLORS = {
    "primary": "$primary",
    "secondary": "$secondary",
    "accent": "$accent",
    "success": "$success",
    "warning": "$warning",
    "error": "$error",
}

BORDER_STYLES = [
    "ascii",
    "blank",
    "dashed",
    "double",
    "heavy",
    "hidden",
    "hkey",
    "inner",
    "none",
    "outer",
    "round",
    "solid",
    "tall",
    "vkey",
    "wide",
]

FRACTIONS = {
    "1/2": "50%",
    "1/3": "33.333333%",
    "2/3": "66.666667%",
    "1/4": "25%",
    "2/4": "50%",
    "3/4": "75%",
    "1/5": "20%",
    "2/5": "40%",
    "3/5": "60%",
    "4/5": "80%",
    "1/6": "16.666667%",
    "2/6": "33.333333%",
    "3/6": "50%",
    "4/6": "66.666667%",
    "5/6": "83.333333%",
    "full": "100%",
}


class TuiStyleGenerator:
    """Generate utility CSS classes for the Textual TUI framework."""

    def __init__(self) -> None:
        """Initialize the style generator with an empty styles list."""
        self.styles: list[str] = []

    def add_style(self, selector: str, *properties: str) -> None:
        """Add a CSS rule to the styles list."""
        props = "; ".join(properties) + ";"
        self.styles.append(f"{selector} {{{props}}}")

    def add_styles(self, styles_dict: dict[str, list[str]]) -> None:
        """Add multiple CSS rules from a dictionary of selectors to properties."""
        for selector, properties in styles_dict.items():
            self.add_style(selector, *properties)

    def add_section_header(self, title: str) -> None:
        """Add a section header comment to the styles."""
        self.styles.append("")
        self.styles.append("# " + "#" * 5)
        self.styles.append(f"# {title}")
        self.styles.append("# " + "#" * 5)
        self.styles.append("")

    def generate_text_alignment(self) -> None:
        """Generate text alignment utility classes."""
        self.add_section_header("Text Alignment")
        for direction in "left|start|center|right|end|justify".split("|"):
            self.add_style(f".text-{direction}", f"text-align: {direction}")

    def generate_spacing(self, max_value: int = 25) -> None:
        """Generate margin and padding utility classes."""
        self.add_section_header("Margins")

        for pix in range(max_value + 1):
            # All-direction margin
            self.add_style(f".m-{pix}", f"margin: {pix}")

            # Horizontal and vertical margins
            self.add_style(f".mx-{pix}", f"margin-left: {pix}", f"margin-right: {pix}")
            self.add_style(f".my-{pix}", f"margin-top: {pix}", f"margin-bottom: {pix}")

            # Individual margin directions
            self.add_style(f".mt-{pix}", f"margin-top: {pix}")
            self.add_style(f".mb-{pix}", f"margin-bottom: {pix}")
            self.add_style(f".ml-{pix}", f"margin-left: {pix}")
            self.add_style(f".mr-{pix}", f"margin-right: {pix}")

        self.add_section_header("Padding")

        for pix in range(max_value + 1):
            # All-direction padding
            self.add_style(f".p-{pix}", f"padding: {pix}")

            # Horizontal and vertical padding
            self.add_style(f".px-{pix}", f"padding-left: {pix}", f"padding-right: {pix}")
            self.add_style(f".py-{pix}", f"padding-top: {pix}", f"padding-bottom: {pix}")

            # Individual padding directions
            self.add_style(f".pt-{pix}", f"padding-top: {pix}")
            self.add_style(f".pb-{pix}", f"padding-bottom: {pix}")
            self.add_style(f".pl-{pix}", f"padding-left: {pix}")
            self.add_style(f".pr-{pix}", f"padding-right: {pix}")

    def generate_dimensions(self, max_value: int = 8) -> None:
        """Generate height and width utility classes."""
        self.add_section_header("Dimensions")

        for pix in range(max_value + 1):
            self.add_style(f".h-{pix}", f"height: {pix}")
            self.add_style(f".w-{pix}", f"width: {pix}")

        # Cases like w-auto, h-auto
        self.add_style(".w-auto", "width: auto")
        self.add_style(".h-auto", "height: auto")

        self.add_style(".w-full", "width: 100%")
        self.add_style(".h-full", "height: 100%")

    def generate_text_color_styles(self) -> None:
        """Generate text color utility classes."""
        self.add_section_header("Text Colors")

        colors = {**COLORS, "muted": "$text-muted"}
        for k, v in colors.items():
            self.add_style(f".text-{k}", f"color: {v}")
            self.add_style(f".text-{k}-90", f"color: {v} 90%")
            self.add_style(f".text-{k}-70", f"color: {v} 70%")
            self.add_style(f".text-{k}-50", f"color: {v} 50%")
            self.add_style(f".text-{k}-30", f"color: {v} 30%")
            self.styles.append("")

    def generate_background_styles(self) -> None:
        """Generate background utility classes."""
        self.add_section_header("Backgrounds")

        colors = {**COLORS, "background": "$background"}
        for k, v in colors.items():
            self.add_style(f".bg-{k}", f"background: {v}")

    def generate_border_styles(self) -> None:
        """Generate border utility classes."""
        self.add_section_header("Borders")
        for k, v in COLORS.items():
            for border in BORDER_STYLES:
                self.add_style(f".border-{border}-{k}", f"border: {border} {v}")
                self.add_style(f".border-l-{border}-{k}", f"border-left: {border} {v}")
                self.add_style(f".border-r-{border}-{k}", f"border-right: {border} {v}")
                self.add_style(f".border-t-{border}-{k}", f"border-top: {border} {v}")
                self.add_style(f".border-b-{border}-{k}", f"border-bottom: {border} {v}")
                self.add_style(
                    f".border-x-{border}-{k}",
                    f"border-left: {border} {v}",
                    f"border-right: {border} {v}",
                )
                self.add_style(
                    f".border-y-{border}-{k}",
                    f"border-top: {border} {v}",
                    f"border-bottom: {border} {v}",
                )

    def generate_general_utilities(self) -> None:
        """Generate general reset CSS utilities."""
        self.add_section_header("General Reset")

        general_styles = {
            "*": [
                "scrollbar-color: $secondary 30%",
                "scrollbar-color-hover: $secondary 50%",
                "scrollbar-color-active: $secondary 80%",
                "scrollbar-background: $surface-darken-1",
                "scrollbar-background-hover: $surface-darken-1",
                "scrollbar-background-active: $surface-darken-1",
                "scrollbar-size-vertical: 1",
                "link-style: none",
                "link-color-hover: $secondary",
                "link-background-hover: $primary 0%",
                "link-style-hover: u not dim bold",
            ],
            ".layout-horizontal": ["layout: horizontal"],
            ".layout-vertical": ["layout: vertical"],
            ".overflow-hidden": ["overflow: hidden hidden"],
        }
        self.add_styles(general_styles)

    def generate_dock_utilities(self) -> None:
        """Generate dock direction utility classes."""
        self.add_section_header("Dock")
        for direction in "top|right|bottom|left".split("|"):
            self.add_style(f".dock-{direction}", f"dock: {direction}")

    def generate_visibility_utilities(self) -> None:
        """Generate visibility utility classes."""
        self.add_section_header("Visibility")
        for vis in "visible|hidden".split("|"):
            self.add_style(f".{vis}", f"visibility: {vis}")

    def generate_text_style_utilities(self) -> None:
        """Generate text style utility classes."""
        self.add_section_header("Text Styles")
        for font in ["bold", "italic", "reverse", "underline", "strike"]:
            self.add_style(f".{font}", f"text-style: {font}")

    def generate_all(self, max_spacing: int = 5, max_dimensions: int = 5) -> str:
        """Generate all utility styles and return as a string."""
        self.styles = []

        self.generate_general_utilities()

        self.generate_dock_utilities()
        self.generate_visibility_utilities()
        self.generate_text_style_utilities()

        self.generate_text_color_styles()

        self.generate_text_alignment()

        # self.generate_border_styles()

        self.generate_spacing(max_spacing)

        # self.generate_dimensions(max_dimensions)
        # self.generate_background_styles()

        return "\n".join(self.styles) + "\n"

    def write_to_file(self, output_path: Path) -> None:
        """Write generated styles to a file."""
        content = self.generate_all()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"TUI styles written to {output_path}")


def main() -> None:
    """Entry point for the script."""
    generator = TuiStyleGenerator()
    output_file = Path(__file__).parent / "utils.tcss"
    generator.write_to_file(output_file)


if __name__ == "__main__":
    main()
