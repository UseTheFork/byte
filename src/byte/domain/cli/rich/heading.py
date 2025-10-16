from rich import box
from rich.markdown import Heading as BaseHeading
from rich.panel import Panel
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
