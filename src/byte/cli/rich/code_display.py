from rich.console import Console, ConsoleOptions, RenderResult
from rich.syntax import Syntax
from rich.text import Text


class CodeDisplay:
    """A Rich renderable that displays code with a left border character on each line.

    Displays code with `▌ ` prefix on each line, providing a visual left border.
    Can optionally apply syntax highlighting.

    Usage: `display = CodeDisplay(code, language="python")`
    """

    def __init__(
        self,
        code: str,
        language: str = "python",
        line_numbers: bool = False,
        word_wrap: bool = True,
        theme: str = "monokai",
    ):
        """Initialize the code display.

        Args:
            code: The code content to display
            language: Programming language for syntax highlighting
            line_numbers: Whether to show line numbers
            word_wrap: Whether to wrap long lines
            theme: Syntax highlighting theme
        """
        self.code = code
        self.language = language
        self.line_numbers = line_numbers
        self.word_wrap = word_wrap
        self.theme = theme

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Render the code with left border characters.

        Args:
            console: Rich console instance
            options: Console rendering options

        Yields:
            Text objects for each line with border prefix
        """
        # Create syntax-highlighted version if language is specified
        if self.language and self.language != "text":
            syntax = Syntax(
                self.code,
                self.language,
                line_numbers=self.line_numbers,
                word_wrap=self.word_wrap,
                theme=self.theme,
            )
            # Render syntax to get highlighted lines
            rendered_lines = console.render_lines(syntax, options)

            # Add border to each rendered line
            for segments in rendered_lines:
                line_text = Text.from_markup("[secondary]▌ [/secondary]")
                for segment in segments:
                    line_text.append(segment.text, segment.style)
                yield line_text
        else:
            # Plain text rendering with border
            lines = self.code.split("\n")
            for line in lines:
                yield Text.from_markup(f"[secondary]▌ [/secondary]{line}")
