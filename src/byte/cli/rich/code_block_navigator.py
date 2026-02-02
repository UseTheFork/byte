from typing import Optional

import click
from rich import get_console
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax

from byte.clipboard.schemas import CodeBlock


class CodeBlockNavigator:
    """Interactive navigator for code blocks with left/right navigation.

    Displays one code block at a time with syntax highlighting, allowing
    navigation between blocks and selection for clipboard copying.
    Usage: `navigator = CodeBlockNavigator(blocks); selected = navigator.navigate()`
    """

    def __init__(
        self,
        blocks: list[CodeBlock],
        console: Optional[Console] = None,
        transient: bool = True,
    ):
        self.blocks = blocks
        self.console = console if console is not None else get_console()
        self.transient = transient
        # Start at most recent (last block)
        self.index = len(blocks) - 1 if blocks else 0

    def _get_action(self) -> str | None:
        """Map keyboard input to navigation actions.

        Returns action name or None if input not recognized.

        Usage: `action = self._get_action()` -> "confirm", "left", "right", "cancel"
        """
        match click.getchar():
            case "\r":
                return "confirm"
            case "\x1b[D" | "a" | "A" | "àK" | "h":
                return "left"
            case "\x1b[C" | "d" | "D" | "àM" | "l":
                return "right"
            case "\x1b":
                return "cancel"
            case _:
                return None

    def _render_block(self) -> Panel:
        """Render the current code block as a Rich Panel.

        Creates a syntax-highlighted panel with truncated content based on
        terminal height, showing metadata in the title.

        Usage: `panel = self._render_block()` -> display current block
        """
        if not self.blocks:
            return Panel(
                "[yellow]No code blocks available[/yellow]",
                title="Code Blocks",
                border_style="secondary",
            )

        block = self.blocks[self.index]

        # Calculate available height for content
        # Account for: panel borders (2), title (1), padding (2), navigation hint (1)
        reserved_lines = 6
        max_content_lines = max(5, self.console.height - reserved_lines)

        # Get lines and truncate if needed
        lines = block.content.split("\n")
        total_lines = len(lines)

        if total_lines > max_content_lines:
            truncated_lines = lines[:max_content_lines]
            content = "\n".join(truncated_lines) + "\n..."
            truncated = True
        else:
            content = block.content
            truncated = False

        # Create syntax-highlighted content
        syntax = Syntax(
            content,
            block.language if block.language != "text" else "python",
            line_numbers=False,
            word_wrap=True,
        )

        # Build title with metadata
        title_parts = [
            f"[bold][{self.index + 1}/{len(self.blocks)}][/bold]",
            f"[{block.language}]",
            f"{total_lines} lines",
        ]
        if truncated:
            title_parts.append("[yellow](truncated)[/yellow]")

        title = " ".join(title_parts)

        return Panel(
            syntax,
            title=title,
            title_align="left",
            border_style="secondary",
            subtitle="[muted]←  →  navigate | Enter copy | Esc cancel[/muted]",
            subtitle_align="center",
        )

    def _move_left(self) -> None:
        """Move to previous code block, wrapping to end if at start."""
        if self.blocks:
            self.index = (self.index - 1) % len(self.blocks)

    def _move_right(self) -> None:
        """Move to next code block, wrapping to start if at end."""
        if self.blocks:
            self.index = (self.index + 1) % len(self.blocks)

    def navigate(self) -> CodeBlock | None:
        """Start interactive navigation and return selected block.

        Displays code blocks one at a time with left/right navigation.
        Returns selected block on Enter, None on Esc or if no blocks available.

        Usage: `selected = navigator.navigate()` -> get user's selection
        """
        if not self.blocks:
            return None

        with Live(
            self._render_block(),
            auto_refresh=False,
            console=self.console,
            transient=self.transient,
        ) as live:
            live.update(self._render_block(), refresh=True)

            while True:
                try:
                    action = self._get_action()

                    if action == "confirm":
                        return self.blocks[self.index]

                    if action == "cancel":
                        raise KeyboardInterrupt

                    if action == "left":
                        self._move_left()
                        live.update(self._render_block(), refresh=True)

                    if action == "right":
                        self._move_right()
                        live.update(self._render_block(), refresh=True)

                except (KeyboardInterrupt, EOFError):
                    return None
