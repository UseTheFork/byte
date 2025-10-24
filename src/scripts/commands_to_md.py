"""Generate commands.md documentation from registered commands.

This script bootstraps the application to access the CommandRegistry,
extracts command metadata, and generates formatted markdown documentation.

Usage: `uv run python src/scripts/commands_to_md.py`
"""

import asyncio
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from byte.bootstrap import bootstrap, shutdown
from byte.core.config.config import ByteConfg
from byte.domain.cli.service.command_registry import Command, CommandRegistry


def group_commands_by_category(commands: Dict[str, Command]) -> Dict[str, List[tuple[str, Command]]]:
	"""Group commands by their category property.

	Returns a dictionary mapping category names to lists of (name, command) tuples.
	Commands are sorted alphabetically within each category.

	Usage: `group_commands_by_category(registry._slash_commands)` -> {"General": [(...), ...]}
	"""
	by_category: Dict[str, List[tuple[str, Command]]] = defaultdict(list)

	for name, command in commands.items():
		category = getattr(command, "category", "General")
		by_category[category].append((name, command))

	# Sort commands within each category
	for category in by_category:
		by_category[category].sort(key=lambda x: x[0])

	return dict(by_category)


def create_commands_markdown(slash_commands: Dict[str, Command]) -> str:
	"""Generate markdown documentation for all registered commands.

	Creates a structured document with commands grouped by category,
	showing command syntax and descriptions.

	Usage: `create_commands_markdown(registry._slash_commands)` -> markdown string
	"""
	lines = [
		"# Commands\n",
		"Byte provides a comprehensive set of commands for interacting with your codebase, managing context, and controlling the AI assistant. Commands are organized by category for easy reference.\n",
		"---\n",
		"",
	]

	# Add hardcoded subprocess command
	lines.append("## System\n")
	lines.append("`!<command>` - Execute a shell command and optionally add output to conversation context\n")
	lines.append("")

	# Group commands by category
	by_category = group_commands_by_category(slash_commands)

	# Generate sections for each category
	for category in sorted(by_category.keys()):
		lines.append(f"## {category}\n")

		for name, command in by_category[category]:
			lines.append(f"`/{name}` - {command.description}\n")

		lines.append("")

	return "\n".join(lines)


async def generate_commands_md() -> None:
	"""Generate commands.md from registered commands.

	Bootstraps the application, extracts command information from the registry,
	and writes formatted markdown to docs/reference/commands.md.

	Usage: `await generate_commands_md()`
	"""
	# Bootstrap minimal app to get registry
	config = ByteConfg()
	container = await bootstrap(config)

	try:
		# Get the registry with all registered commands
		registry = await container.make(CommandRegistry)

		# Generate markdown content
		markdown = create_commands_markdown(registry._slash_commands)

		# Write to docs/reference/commands.md
		output_file = Path(__file__).parent.parent.parent / "docs" / "reference" / "commands.md"
		output_file.parent.mkdir(parents=True, exist_ok=True)
		output_file.write_text(markdown, encoding="utf-8")

		print(f"Commands documentation written to {output_file}")

	finally:
		await shutdown(container)


def main():
	"""Entry point for the script.

	Usage: `python src/scripts/commands_to_md.py`
	"""
	asyncio.run(generate_commands_md())


if __name__ == "__main__":
	main()
