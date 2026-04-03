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
    """Generator for Textual CSS utility classes.

    Generates utility classes for common CSS properties like margins,
    padding, text alignment, dimensions, etc.
    """

    def __init__(self):
        """Initialize the style generator with an empty styles list."""
        self.styles: list[str] = []

    def add_style(self, selector: str, *properties: str) -> None:
        """Add a CSS rule to the styles list.

        Args:
            selector: CSS selector (e.g., ".mt-1")
            *properties: CSS property declarations (e.g., "margin-top: 1")

        Usage: `generator.add_style(".mt-1", "margin-top: 1")`
        """
        props = "; ".join(properties) + ";"
        self.styles.append(f"{selector} {{{props}}}")

    def add_section_header(self, title: str) -> None:
        """Add a section header comment to the styles.

        Args:
            title: Section title

        Usage: `generator.add_section_header("Margins")`
        """
        self.styles.append("")
        self.styles.append("# " + "#" * 5)
        self.styles.append(f"# {title}")
        self.styles.append("# " + "#" * 5)
        self.styles.append("")

    def generate_text_alignment(self) -> None:
        """Generate text alignment utility classes.

        Creates classes like .text-left, .text-center, .text-right, etc.
        """
        self.add_section_header("Text Alignment")
        for direction in "left|start|center|right|end|justify".split("|"):
            self.add_style(f".text-{direction}", f"text-align: {direction}")

    def generate_spacing(self, max_value: int = 25) -> None:
        """Generate margin and padding utility classes.

        Args:
            max_value: Maximum value for spacing utilities (0 to max_value inclusive)

        Creates classes for margins and padding in all directions.
        """
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
        """Generate height and width utility classes.

        Args:
            max_value: Maximum value for dimension utilities (0 to max_value inclusive)

        Creates classes like .h-1, .w-2, etc.
        """
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
        """Generate text color utility classes.

        Creates classes for text colors.
        """
        self.add_section_header("Text Colors")
        for k, v in COLORS.items():
            self.add_style(f".text-{k}", f"color: $text-{k}")

    def generate_background_styles(self) -> None:
        """Generate background utility classes.

        Creates classes for background colors.
        """
        self.add_section_header("Backgrounds")

        colors = {**COLORS, "background": "$background"}
        for k, v in colors.items():
            self.add_style(f".bg-{k}", f"background: {v}")

    def generate_border_styles(self) -> None:
        """Generate border utility classes.

        Creates classes for borders with various styles.
        """
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

    def generate_dock_utilities(self) -> None:
        """Generate dock direction utility classes.

        Creates classes like .dock-top, .dock-right, .dock-bottom, .dock-left.
        """
        self.add_section_header("Dock")
        for direction in "top|right|bottom|left".split("|"):
            self.add_style(f".dock-{direction}", f"dock: {direction}")

    def generate_visibility_utilities(self) -> None:
        """Generate visibility utility classes.

        Creates classes like .visible and .hidden.
        """
        self.add_section_header("Visibility")
        for vis in "visible|hidden".split("|"):
            self.add_style(f".{vis}", f"visibility: {vis}")

    def generate_text_style_utilities(self) -> None:
        """Generate text style utility classes.

        Creates classes like .bold, .italic, .reverse, .underline, .strike.
        """
        self.add_section_header("Text Styles")
        for font in ["bold", "italic", "reverse", "underline", "strike"]:
            self.add_style(f".{font}", f"text-style: {font}")

    def generate_all(self, max_spacing: int = 8, max_dimensions: int = 10) -> str:
        """Generate all utility styles and return as a string.

        Args:
            max_spacing: Maximum value for margin/padding utilities
            max_dimensions: Maximum value for height/width utilities

        Returns:
            Complete CSS stylesheet as a string

        Usage: `css_content = generator.generate_all()`
        """
        self.styles = []

        self.generate_text_alignment()
        self.generate_spacing(max_spacing)
        self.generate_dimensions(max_dimensions)
        self.generate_text_color_styles()
        self.generate_background_styles()
        self.generate_border_styles()
        self.generate_dock_utilities()
        self.generate_visibility_utilities()
        self.generate_text_style_utilities()

        return "\n".join(self.styles) + "\n"

    def write_to_file(self, output_path: Path) -> None:
        """Write generated styles to a file.

        Args:
            output_path: Path to the output file

        Usage: `generator.write_to_file(Path("src/byte/tui/tui.tcss"))`
        """
        content = self.generate_all()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"TUI styles written to {output_path}")


def main():
    """Entry point for the script.

    Usage: `python src/scripts/generate_tui_styles.py`
    """
    generator = TuiStyleGenerator()
    output_file = Path(__file__).parent / "tui.tcss"
    generator.write_to_file(output_file)


if __name__ == "__main__":
    main()
