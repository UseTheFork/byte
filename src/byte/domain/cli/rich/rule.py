from typing import Union

from rich.align import AlignMethod
from rich.rule import Rule as RulePanel
from rich.style import Style
from rich.text import Text


class Rule(RulePanel):
	"""Custom Rule component with modified default alignment.

	Inherits from Rich's Rule but changes the default alignment to 'left'
	instead of 'center' for consistent styling with the project.
	Usage: `Rule("Title")` -> creates left-aligned rule with title
	"""

	def __init__(
		self,
		title: Union[str, Text] = "",
		*,
		characters: str = "─",
		style: Union[str, Style] = "rule.line",
		end: str = "\n",
		align: AlignMethod = "left",
	) -> None:
		"""Initialize Rule with custom default alignment.

		Args:
			title: Title text to display in the rule
			characters: Characters to use for the rule line
			style: Style for the rule line
			end: String to append after rule
			align: Alignment of the title (default: 'left')
		"""
		super().__init__(
			title=title,
			characters=characters,
			style=style,
			end=end,
			align=align,
		)
