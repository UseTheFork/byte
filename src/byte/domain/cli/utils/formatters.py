import asyncio
import io

from rich import box
from rich.console import Console
from rich.live import Live
from rich.markdown import CodeBlock, Heading, Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text


# Credits to aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/mdstream.py
class NoInsetCodeBlock(CodeBlock):
	"""A code block with syntax highlighting and no padding."""

	def __rich_console__(self, console, options):
		code = str(self.text).rstrip()
		syntax = Syntax(code, self.lexer_name, theme=self.theme, word_wrap=True, padding=(1, 0))
		yield syntax


class LeftHeading(Heading):
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


class NoInsetMarkdown(Markdown):
	"""Markdown with code blocks that have no padding and left-justified headings."""

	elements = {
		**Markdown.elements,
		"fence": NoInsetCodeBlock,
		"code_block": NoInsetCodeBlock,
		"heading_open": LeftHeading,
	}


class MarkdownStream:
	"""Streaming markdown renderer that progressively displays content with a live updating window.

	Uses rich.console and rich.live to render markdown content with smooth scrolling
	and partial updates. Maintains a sliding window of visible content while streaming
	in new markdown text.
	"""

	live = None  # Rich Live display instance
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
		markdown = NoInsetMarkdown(text, **self.mdargs)
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
				self.live.console.print(stable_display)

			# Update our record of printed lines
			self.printed = lines_chunk[:stable_lines]

		# Update live window with remaining unstable lines
		if not is_final:
			remaining_lines = lines_chunk[stable_lines:]
			if remaining_lines:
				live_text = "".join(remaining_lines)
				live_display = Text.from_ansi(live_text)
				self.live.update(live_display)

		if is_final and self.live:
			self.live.update(Text(""))
			self.live.stop()
			self.live = None
