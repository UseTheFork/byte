from typing import TYPE_CHECKING, Optional

from rich.align import AlignMethod
from rich.box import ROUNDED, Box
from rich.padding import PaddingDimensions
from rich.panel import Panel as BasePanel
from rich.style import StyleType
from rich.text import TextType

if TYPE_CHECKING:
	from rich.console import RenderableType


class Panel(BasePanel):
	"""Custom Panel class that extends Rich's BasePanel with modified default styling.

	This Panel class provides a wrapper around Rich's Panel component with customized
	default values for title alignment (left instead of center) and border style
	(inactive_border instead of none).
	"""

	def __init__(
		self,
		renderable: "RenderableType",
		box: Box = ROUNDED,
		*,
		title: Optional[TextType] = None,
		title_align: AlignMethod = "left",
		subtitle: Optional[TextType] = None,
		subtitle_align: AlignMethod = "left",
		safe_box: Optional[bool] = None,
		expand: bool = True,
		style: StyleType = "none",
		border_style: StyleType = "inactive_border",
		width: Optional[int] = None,
		height: Optional[int] = None,
		padding: PaddingDimensions = (0, 1),
		highlight: bool = False,
	) -> None:
		super().__init__(
			renderable,
			box=box,
			title=title,
			title_align=title_align,
			subtitle=subtitle,
			subtitle_align=subtitle_align,
			safe_box=safe_box,
			expand=expand,
			style=style,
			border_style=border_style,
			width=width,
			height=height,
			padding=padding,
			highlight=highlight,
		)
