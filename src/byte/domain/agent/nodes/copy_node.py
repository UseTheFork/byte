import re

import pyperclip
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command
from rich.columns import Columns

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import extract_content_from_message
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService


class CopyNode(Node, UserInteractive):
	"""Node for extracting and copying code blocks to clipboard.

	Parses code blocks from the last message, displays truncated previews,
	and allows user to select which block to copy to clipboard.
	Usage: Used in CopyAgent workflow via `/copy` command
	"""

	async def __call__(self, state: BaseState, config: RunnableConfig):
		"""Extract code blocks and prompt user to select one for clipboard copy."""
		console = await self.make(ConsoleService)
		messages = state["messages"]
		last_message = messages[-1]

		response_text = extract_content_from_message(last_message)

		# Extract all code blocks with their language identifiers
		code_blocks = self._extract_code_blocks(response_text)

		if not code_blocks:
			console.print_warning("No code blocks found in the last message.")
			return Command(goto="end_node", update=state)

		# Display truncated previews and let user select
		selected_block = await self._prompt_user_selection(code_blocks)

		if selected_block is not None:
			# Copy to clipboard
			pyperclip.copy(selected_block["content"])
			console.print_success(f"Copied {selected_block['language']} code block to clipboard!")

		return Command(goto="end_node", update=state)

	def _extract_code_blocks(self, content: str) -> list[dict[str, str]]:
		"""Extract all code blocks from content with their language identifiers.

		Args:
			content: Text content containing code blocks

		Returns:
			List of dicts with 'language' and 'content' keys

		Usage: `blocks = self._extract_code_blocks(message_text)`
		"""
		# Pattern to match code blocks: ```language\ncontent\n```
		pattern = r"```(\w*)\n(.*?)```"
		matches = re.findall(pattern, content, re.DOTALL)

		blocks = []
		for language, code_content in matches:
			# Use "text" as default language if not specified
			lang = language if language else "text"
			blocks.append({"language": lang, "content": code_content.strip()})

		return blocks

	async def _prompt_user_selection(self, code_blocks: list[dict[str, str]]) -> dict[str, str] | None:
		"""Display truncated code blocks in panels and prompt user to select one.

		Args:
			code_blocks: List of code block dicts with 'language' and 'content'

		Returns:
			Selected code block dict or None if cancelled

		Usage: `block = await self._prompt_user_selection(blocks)`
		"""

		console = await self.make(ConsoleService)

		# Configuration for preview display
		max_preview_lines = 5

		# Calculate max line length based on console width to fit 2 columns
		# Account for: panel borders (4 chars per panel), column gap (3 chars), and padding (4 chars per panel)
		console_width = console.width
		padding_per_panel = 8  # 4 chars for borders + 4 chars for internal padding
		column_gap = 3
		total_overhead = (padding_per_panel * 2) + column_gap
		max_line_length = max(40, (console_width - total_overhead) // 2)

		# Build panels for each code block
		panels = []
		choices = []

		for idx, block in enumerate(code_blocks):
			lang = block["language"]
			content = block["content"]

			# Get first few lines for preview
			lines = content.split("\n")
			preview_lines = lines[:max_preview_lines]

			# Truncate long lines
			truncated_lines = []
			for line in preview_lines:
				if len(line) > max_line_length:
					truncated_lines.append(line[:max_line_length] + "...")
				else:
					truncated_lines.append(line)

			preview_content = "\n".join(truncated_lines)

			# Add ellipsis if there are more lines
			if len(lines) > max_preview_lines:
				preview_content += "\n..."

			# Create syntax-highlighted preview
			syntax = console.syntax(
				preview_content,
				lang if lang != "text" else "python",
				line_numbers=False,
				word_wrap=True,
			)

			# Create panel for this code block
			panel = console.panel(
				syntax,
				title=f"{idx + 1}. [{lang}] {len(lines)} lines",
				border_style="secondary",
			)
			panels.append(panel)

			# Store choice text for selection (without preview content)
			choices.append(f"[{lang}] {len(lines)} lines")

		# Add cancel option
		cancel_panel = console.panel(
			"[yellow]Don't copy anything[/yellow]",
			title=f"[bold]{len(code_blocks) + 1}. Cancel[/bold]",
			border_style="red",
		)
		panels.append(cancel_panel)
		choices.append("[Cancel] Don't copy anything")

		# Display panels in columns (2 columns for better layout)
		console.print()
		console.rule("Select a code block to copy")
		console.print()
		console.print(Columns(panels, equal=True, expand=True))

		# Prompt user to select
		selected = await self.prompt_for_select_numbered(
			"\nEnter number to copy",
			choices,
			default=None,
		)

		# If user selected cancel or invalid choice
		if selected == choices[-1] or selected not in choices:
			return None

		# Return the selected block
		selected_idx = choices.index(selected)
		return code_blocks[selected_idx]
