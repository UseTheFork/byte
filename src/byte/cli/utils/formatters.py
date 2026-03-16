import asyncio
import io
import re

from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.theme import Theme

from byte.cli import Markdown
from byte.support import BoundaryType


class MarkdownStream:
    """Streaming markdown renderer that progressively displays content with a live updating window.

    Uses rich.console and rich.live to render markdown content with smooth scrolling
    and partial updates. Maintains a sliding window of visible content while streaming
    in new markdown text.
    """

    live: Live | None = None  # Rich Live display instance
    live_window = 6  # Number of lines to keep visible at bottom during streaming

    def __init__(self, console: Console, rich_theme: Theme, mdargs=None):
        """Initialize the markdown stream.

        Args:
                mdargs (dict, optional): Additional arguments to pass to rich Markdown renderer
        """
        self.printed = []  # Stores lines that have already been printed

        if mdargs:
            self.mdargs = mdargs
        else:
            self.mdargs = dict()

        # Defer Live creation until the first update.
        self.console = console
        self.rich_theme = rich_theme
        self.live = None
        self._live_started = False

    def __del__(self):
        """Destructor to ensure Live display is properly cleaned up."""
        if self.live:
            try:
                self.live.stop()
            except Exception:
                pass  # Ignore any errors during cleanup

    def _preprocess_tags(self, text: str) -> str:
        """Convert <agent_plan> tags to markdown with visual separators."""

        # Replace opening tag with a visual header
        text = re.sub(rf"<{BoundaryType.PLAN}>", "```byte\n Agent Plan\n```", text)
        text = re.sub(rf"</{BoundaryType.PLAN}>", "", text)

        # Replace operation_block opening tags with code fences using file extension as lexer
        def replace_operation_block_open(match):
            # Extract the full opening tag
            full_tag = match.group(0)

            # Extract attributes
            path_match = re.search(r'path="([^"]*)"', full_tag)
            operation_match = re.search(r'operation="([^"]*)"', full_tag)
            block_id_match = re.search(r'block_id="([^"]*)"', full_tag)

            # Build metadata header
            metadata_parts = ["```byte"]
            if block_id_match:
                metadata_parts.append(f" Block ID: {block_id_match.group(1)}")
            if operation_match:
                metadata_parts.append(f" Operation: `{operation_match.group(1)}`")
            if path_match:
                metadata_parts.append(f" Path: `{path_match.group(1)}`")
            metadata_parts.append("```")

            # Determine lexer from file extension
            extension = "text"
            if path_match:
                file_path = path_match.group(1)
                extension = file_path.split(".")[-1] if "." in file_path else "text"

            # Build result with metadata header above code fence
            if metadata_parts:
                metadata_header = "\n".join(metadata_parts)
                return f"{metadata_header}\n```{extension}\n"

            # Fallback to text if no metadata found
            return f"```{extension}\n"

        # Replace opening tags
        text = re.sub(rf"<{BoundaryType.EDIT_BLOCK}\s+[^>]*>", replace_operation_block_open, text)

        # <<<<<<<, =======, >>>>>>>
        text = re.sub(rf"<{BoundaryType.SEARCH}>", "<<<<<<< SEARCH", text)
        text = re.sub(rf"</{BoundaryType.SEARCH}>", "=======", text)
        text = re.sub(rf"<{BoundaryType.REPLACE}>", "", text)
        text = re.sub(rf"</{BoundaryType.REPLACE}>", ">>>>>>> REPLACE", text)

        # Replace closing tags
        text = re.sub(rf"</{BoundaryType.EDIT_BLOCK}>", "```", text)

        return text

    def _render_markdown_to_lines(self, text):
        """Render markdown text to a list of lines.

        Args:
                text (str): Markdown text to render

        Returns:
                list: List of rendered lines with line endings preserved
        """
        # Pre-process agent tags
        text = self._preprocess_tags(text)

        # Render the markdown to a string buffer
        string_io = io.StringIO()
        console = Console(file=string_io, force_terminal=True, theme=self.rich_theme)
        markdown = Markdown(text, **self.mdargs)
        console.print(markdown)
        output = string_io.getvalue()

        # Split rendered output into lines
        return output.splitlines(keepends=True)

    async def _process_line_chunk(self, lines_chunk, is_final):
        """Process chunk of lines without blocking"""
        if not self._live_started:
            self.live = Live(Text(""), console=self.console, refresh_per_second=20)
            self.live.start()
            self._live_started = True

        # lines_chunk contains ALL lines from accumulated content
        # We need to figure out what's new since last time
        total_lines = len(lines_chunk)
        num_already_printed = len(self.printed)

        if not is_final:
            # Keep some lines in the live window for updates
            stable_lines = max(0, total_lines - self.live_window)
        else:
            # If final, all lines are stable
            stable_lines = total_lines

        # Calculate how many new stable lines to print above live window
        new_stable_count = stable_lines - num_already_printed

        if new_stable_count > 0:
            # Print only the NEW stable lines above the live window
            new_stable_lines = lines_chunk[num_already_printed:stable_lines]
            stable_text = "".join(new_stable_lines)
            if stable_text:
                stable_display = Text.from_ansi(stable_text)
                if self.live and self.live.console:
                    self.live.console.print(stable_display)

            # Update our record of printed lines
            self.printed = lines_chunk[:stable_lines]

        # Update live window with remaining unstable lines
        if not is_final:
            remaining_lines = lines_chunk[stable_lines:]
            if remaining_lines:
                live_text = "".join(remaining_lines)
                live_display = Text.from_ansi(live_text)
                if self.live:
                    self.live.update(live_display)

        if is_final and self.live:
            self.live.update("")
            self.live.stop()
            self.live = None

    async def update(self, text: str, final: bool = False):
        """Async version of update that yields control"""
        # Process all lines at once like the original update method
        lines = self._render_markdown_to_lines(text)

        # Process all lines without chunking
        await self._process_line_chunk(lines, final)

        # Yield control once
        await asyncio.sleep(0)
