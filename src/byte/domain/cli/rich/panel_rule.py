from typing import Union

from rich.align import AlignMethod
from rich.cells import cell_len, set_cell_size
from rich.console import Console, ConsoleOptions, RenderResult
from rich.jupyter import JupyterMixin
from rich.measure import Measurement
from rich.style import Style
from rich.text import Text


class PanelTop(JupyterMixin):
    """A console renderable to draw the top border of a panel with optional title.

    Args:
        title (Union[str, Text], optional): Text to render in the top border. Defaults to "".
        style (Union[str, Style], optional): Style of the border. Defaults to "none".
        border_style (Union[str, Style], optional): Style of the border line. Defaults to "none".
        align (AlignMethod, optional): How to align the title, one of "left", "center", or "right". Defaults to "center".
    """

    def __init__(
        self,
        title: Union[str, Text] = "",
        *,
        style: Union[str, Style] = "none",
        border_style: Union[str, Style] = "none",
        align: AlignMethod = "center",
    ) -> None:
        if align not in ("left", "center", "right"):
            raise ValueError(f'invalid value for align, expected "left", "center", "right" (not {align!r})')
        self.title = title
        self.style = style
        self.border_style = border_style
        self.align = align

    def __repr__(self) -> str:
        return f"PanelTop({self.title!r})"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        width = options.max_width
        style = console.get_style(self.style)
        border_style = style + console.get_style(self.border_style)

        # Panel characters
        top_left = "╭─"
        top_right = "╮"
        top = "─"

        if not self.title:
            # Simple top border without title
            yield Text(top_left + (top * (width - 2)) + top_right, style=border_style)
            return

        if isinstance(self.title, Text):
            title_text = self.title
        else:
            title_text = console.render_str(self.title, style="none")

        title_text.plain = " " + title_text.plain.replace("\n", " ")
        title_text.expand_tabs()

        required_space = 4 if self.align == "center" else 2
        truncate_width = max(0, width - required_space)
        if not truncate_width:
            yield Text(top_left + (top * (width - 2)) + top_right, style=border_style)
            return

        rule_text = Text()
        if self.align == "center":
            title_text.truncate(truncate_width, overflow="ellipsis")
            side_width = (width - cell_len(title_text.plain)) // 2
            left = Text(top * (side_width - 1))
            left.truncate(side_width - 1)
            right_length = width - cell_len(left.plain) - cell_len(title_text.plain) - 2
            right = Text(top * right_length)
            right.truncate(right_length)
            rule_text.append(top_left, border_style)
            rule_text.append(left.plain, border_style)
            rule_text.append(" ", border_style)
            rule_text.append(title_text)
            rule_text.append(" ", border_style)
            rule_text.append(right.plain, border_style)
            rule_text.append(top_right, border_style)
        elif self.align == "left":
            title_text.truncate(truncate_width, overflow="ellipsis")
            rule_text.append(top_left, border_style)
            rule_text.append(title_text)
            rule_text.append(" ", border_style)
            rule_text.append(top * (width - rule_text.cell_len - 1), border_style)
            rule_text.append(top_right, border_style)
        elif self.align == "right":
            title_text.truncate(truncate_width, overflow="ellipsis")
            rule_text.append(top_left, border_style)
            rule_text.append(top * (width - title_text.cell_len - 3), border_style)
            rule_text.append(" ", border_style)
            rule_text.append(title_text)
            rule_text.append(top_right, border_style)

        rule_text.plain = set_cell_size(rule_text.plain, width)
        yield rule_text

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        return Measurement(1, 1)


class PanelBottom(JupyterMixin):
    """A console renderable to draw the bottom border of a panel with optional subtitle.

    Args:
        subtitle (Union[str, Text], optional): Text to render in the bottom border. Defaults to "".
        style (Union[str, Style], optional): Style of the border. Defaults to "none".
        border_style (Union[str, Style], optional): Style of the border line. Defaults to "none".
        align (AlignMethod, optional): How to align the subtitle, one of "left", "center", or "right". Defaults to "center".
    """

    def __init__(
        self,
        subtitle: Union[str, Text] = "",
        *,
        style: Union[str, Style] = "none",
        border_style: Union[str, Style] = "none",
        align: AlignMethod = "center",
    ) -> None:
        if align not in ("left", "center", "right"):
            raise ValueError(f'invalid value for align, expected "left", "center", "right" (not {align!r})')
        self.subtitle = subtitle
        self.style = style
        self.border_style = border_style
        self.align = align

    def __repr__(self) -> str:
        return f"PanelBottom({self.subtitle!r})"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        width = options.max_width
        style = console.get_style(self.style)
        border_style = style + console.get_style(self.border_style)

        # Panel characters
        bottom_left = "╰"
        bottom_right = "╯"
        bottom = "─"

        if not self.subtitle:
            # Simple bottom border without subtitle
            yield Text(bottom_left + (bottom * (width - 2)) + bottom_right, style=border_style)
            return

        if isinstance(self.subtitle, Text):
            subtitle_text = self.subtitle
        else:
            subtitle_text = console.render_str(self.subtitle, style="none")

        subtitle_text.plain = subtitle_text.plain.replace("\n", " ")
        subtitle_text.expand_tabs()

        required_space = 4 if self.align == "center" else 2
        truncate_width = max(0, width - required_space)
        if not truncate_width:
            yield Text(bottom_left + (bottom * (width - 2)) + bottom_right, style=border_style)
            return

        rule_text = Text()
        if self.align == "center":
            subtitle_text.truncate(truncate_width, overflow="ellipsis")
            side_width = (width - cell_len(subtitle_text.plain)) // 2
            left = Text(bottom * (side_width - 1))
            left.truncate(side_width - 1)
            right_length = width - cell_len(left.plain) - cell_len(subtitle_text.plain) - 2
            right = Text(bottom * right_length)
            right.truncate(right_length)
            rule_text.append(bottom_left, border_style)
            rule_text.append(left.plain, border_style)
            rule_text.append(" ", border_style)
            rule_text.append(subtitle_text)
            rule_text.append(" ", border_style)
            rule_text.append(right.plain, border_style)
            rule_text.append(bottom_right, border_style)
        elif self.align == "left":
            subtitle_text.truncate(truncate_width, overflow="ellipsis")
            rule_text.append(bottom_left, border_style)
            rule_text.append(subtitle_text)
            rule_text.append(" ", border_style)
            rule_text.append(bottom * (width - rule_text.cell_len - 1), border_style)
            rule_text.append(bottom_right, border_style)
        elif self.align == "right":
            subtitle_text.truncate(truncate_width, overflow="ellipsis")
            rule_text.append(bottom_left, border_style)
            rule_text.append(bottom * (width - subtitle_text.cell_len - 3), border_style)
            rule_text.append(" ", border_style)
            rule_text.append(subtitle_text)
            rule_text.append(bottom_right, border_style)

        rule_text.plain = set_cell_size(rule_text.plain, width)
        yield rule_text

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        return Measurement(1, 1)
