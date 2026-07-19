from rich.console import Console, ConsoleOptions, RenderResult
from rich.syntax import Syntax
from rich.text import Text


class ByteDisplay:
    """Render code with a left border character on each line."""

    def __init__(
        self,
        code: str,
        line_numbers: bool = False,
        word_wrap: bool = True,
        theme: str = "monokai",
        padding: int = 1,
    ):
        """Initialize the code display with rendering options."""
        self.code = code
        self.line_numbers = line_numbers
        self.word_wrap = word_wrap
        self.theme = theme
        self.padding = padding

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Render the code with left border characters."""
        # Add padding to the code itself so it becomes part of rendered_lines
        padded_code = "\n" * self.padding + self.code + "\n" * self.padding

        # Create syntax-highlighted version if language is specified
        syntax = Syntax(
            padded_code,
            "markdown",
            line_numbers=self.line_numbers,
            word_wrap=self.word_wrap,
            theme=self.theme,
        )
        # Render syntax to get highlighted lines
        rendered_lines = console.render_lines(syntax, options)

        # Add border to each rendered line
        for segments in rendered_lines:
            line_text = Text.from_markup("[primary]▌[/primary][secondary]▌[/secondary]")
            for segment in segments:
                line_text.append(segment.text, segment.style)
            yield line_text
