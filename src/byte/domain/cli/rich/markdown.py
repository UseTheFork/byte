from rich.markdown import Heading, Markdown as BaseMarkdown

from byte.domain.cli.rich.code_block import CodeBlock


# Credits to aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/mdstream.py
class Markdown(BaseMarkdown):
	"""Markdown with code blocks that have no padding and left-justified headings."""

	elements = {
		**BaseMarkdown.elements,
		"fence": CodeBlock,
		"code_block": CodeBlock,
		"heading_open": Heading,
	}
