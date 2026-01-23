from rich import box
from rich.markdown import CodeBlock as BaseCodeBlock, Heading as BaseHeading, Markdown as BaseMarkdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text


# Credits to aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/mdstream.py
class Heading(BaseHeading):
    """A heading class that renders left-justified."""

    def __rich_console__(self, console, options):
        text = self.text
        text.justify = "left"  # Override justification
        if self.tag == "h1":
            # Draw a border around h1s, but keep text left-aligned
            yield Panel(
                text,
                box=box.ROUNDED,
                style="markdown.h1.border",
            )
        else:
            # Styled text for h2 and beyond
            if self.tag == "h2":
                yield Text("")  # Keep the blank line before h2
            yield text


# Credits to aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/mdstream.py
class CodeBlock(BaseCodeBlock):
    """A code block with syntax highlighting and no padding."""

    def __rich_console__(self, console, options):
        code = str(self.text).rstrip()
        syntax = Syntax(code, self.lexer_name, theme=self.theme, word_wrap=True, padding=(1, 0))
        yield syntax


# Credits to aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/mdstream.py
class Markdown(BaseMarkdown):
    """Markdown with code blocks that have no padding and left-justified headings."""

    elements = {
        **BaseMarkdown.elements,
        "fence": CodeBlock,
        "code_block": CodeBlock,
        "heading_open": Heading,
    }
