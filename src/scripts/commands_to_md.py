"""Generate available-commands.md documentation from registered commands.

This script bootstraps the application to access the CommandRegistry,
extracts command metadata, and generates formatted markdown documentation.

Usage: `uv run python src/scripts/commands_to_md.py`
"""

import argparse
import asyncio
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from byte import Command, CommandRegistryService
from byte.main import PROVIDERS


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


def extract_parameters(command: Command) -> List[str]:
    """Extract parameter documentation from command's parser.

    Returns a list of formatted parameter lines suitable for markdown.
    Identifies argument name, type hints, and required/optional status.

    Usage: `extract_parameters(command)` -> ["- `query` (string, required) — The search query"]
    """
    parser = command.parser
    params = []

    # Filter out help action and other built-in actions
    for action in parser._actions:
        if action.dest == "help":
            continue

        param_name = action.dest
        help_text = action.help or ""

        # Determine if required
        is_required = action.required if hasattr(action, "required") else action.nargs != "?"
        required_str = "required" if is_required else "optional"

        # Determine type
        if action.type:
            type_str = action.type.__name__
        else:
            type_str = "string"

        # Handle nargs
        nargs_info = ""
        if action.nargs == argparse.REMAINDER:
            nargs_info = " (takes all remaining arguments)"
            required_str = "required"
        elif action.nargs == "?":
            required_str = "optional"
        elif action.nargs == "*":
            required_str = "optional"

        params.append(f"- `{param_name}` ({type_str}, {required_str}) — {help_text}{nargs_info}")

    return params or ["None"]


def generate_usage_example(name: str, command: Command) -> str:
    """Generate example usage line for a command.

    Usage: `generate_usage_example("add", command)` -> "/add src/main.py"
    """
    # Check if command has any arguments
    has_args = False
    for action in command.parser._actions:
        if action.dest != "help":
            has_args = True
            break

    if not has_args:
        return f"`/{name}`"

    # Build a simple example based on parser structure
    # For now, return generic pattern
    return f"`/{name}` or `/{name} <args>`"


def create_commands_markdown(slash_commands: Dict[str, Command]) -> str:
    """Generate markdown documentation for all registered commands.

    Creates a structured document with commands grouped by category,
    showing command syntax, parameters, and usage examples in rich format.

    Usage: `create_commands_markdown(registry._slash_commands)` -> markdown string
    """
    lines = []

    # Group commands by category
    by_category = group_commands_by_category(slash_commands)

    # Generate sections for each category
    for category in sorted(by_category.keys()):
        lines.append(f"## {category} Commands")
        lines.append("")

        for name, command in by_category[category]:
            parser = command.parser
            description = parser.description or "No description available"

            # Add command heading and description
            lines.append(f"### /{name}")
            lines.append("")
            lines.append(description)
            lines.append("")

            # Method name
            lines.append(f"**Method name**: `{name}`")
            lines.append("")

            # Parameters section
            lines.append("**Parameters**:")
            lines.append("")
            params = extract_parameters(command)
            for param in params:
                lines.append(param)
            lines.append("")

            # Usage section
            lines.append("**Usage**: " + generate_usage_example(name, command))
            lines.append("")

        lines.append("")

    return "\n".join(lines)


async def generate_commands_md() -> None:
    """Generate available-commands.md from registered commands."""

    from byte import Application
    from byte.foundation import Kernel

    app = Application.configure(Path(__file__).parent, PROVIDERS).create()  # ty:ignore[invalid-argument-type]

    kernel = app.make(Kernel, app=app)
    kernel.bootstrap()

    # Now we can Async boot all the providers
    await kernel.app.boot()

    registry = app.make(CommandRegistryService)

    markdown = create_commands_markdown(registry._slash_commands)

    # Write to docs/explanation/commands.md
    output_file = Path(__file__).parent.parent.parent / "docs" / "references" / "commands.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown, encoding="utf-8")

    print(f"Commands documentation written to {output_file}")


def main():
    """Entry point for the script.

    Usage: `python src/scripts/commands_to_md.py`
    """

    asyncio.run(generate_commands_md())


if __name__ == "__main__":
    main()
