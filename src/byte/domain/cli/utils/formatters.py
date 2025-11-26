import asyncio
import io

from rich.console import Console
from rich.live import Live
from rich.text import Text

from byte.domain.cli.rich.markdown import Markdown


class MarkdownStream:
    """Streaming markdown renderer that progressively displays content with a live updating window.

    Uses rich.console and rich.live to render markdown content with smooth scrolling
    and partial updates. Maintains a sliding window of visible content while streaming
    in new markdown text.
    """

    live: Live | None = None  # Rich Live display instance
    live_window = 6  # Number of lines to keep visible at bottom during streaming

    def __init__(self, console: Console, mdargs=None):
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
        self.live = None
        self._live_started = False

    def _render_markdown_to_lines(self, text):
        """Render markdown text to a list of lines.

        Args:
                text (str): Markdown text to render

        Returns:
                list: List of rendered lines with line endings preserved
        """
        # Render the markdown to a string buffer
        string_io = io.StringIO()
        console = Console(file=string_io, force_terminal=True)
        markdown = Markdown(text, **self.mdargs)
        console.print(markdown)
        output = string_io.getvalue()

        # Split rendered output into lines
        return output.splitlines(keepends=True)

    def __del__(self):
        """Destructor to ensure Live display is properly cleaned up."""
        if self.live:
            try:
                self.live.stop()
            except Exception:
                pass  # Ignore any errors during cleanup

    async def update(self, text: str, final: bool = False):
        """Async version of update that yields control"""
        # Process all lines at once like the original update method
        lines = self._render_markdown_to_lines(text)

        # Process all lines without chunking
        await self._process_line_chunk(lines, final)

        # Yield control once
        await asyncio.sleep(0)

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
