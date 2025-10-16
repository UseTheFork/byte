from rich.markdown import CodeBlock as BaseCodeBlock
from rich.syntax import Syntax


# Credits to aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/mdstream.py
class CodeBlock(BaseCodeBlock):
	"""A code block with syntax highlighting and no padding."""

	def __rich_console__(self, console, options):
		code = str(self.text).rstrip()
		syntax = Syntax(code, self.lexer_name, theme=self.theme, word_wrap=True, padding=(1, 0))
		yield syntax
