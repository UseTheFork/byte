from pathlib import Path

from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel

from byte.context import make
from byte.core.logging import log
from byte.domain.cli_input.service.interactions_service import InteractionService
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.file_service import FileService


@tool(parse_docstring=True)
async def replace_text_in_file(
    file_path: str,
    old_string: str,
    new_string: str,
) -> str:
    """Replaces text within a file. Replaces a single occurrence. This tool requires providing significant context around the change to ensure precise targeting.

    The user has the ability to modify the `new_string` content. If modified, this will be stated in the response.

    Expectation for required parameters:
    1. `file_path` MUST be a path to a file that is in the Editable files context; otherwise an error will be thrown.
    2. `old_string` MUST be the exact literal text to replace (including all whitespace, indentation, newlines, and surrounding code etc.).
    3. `new_string` MUST be the exact literal text to replace `old_string` with (also including all whitespace, indentation, newlines, and surrounding code etc.). Ensure the resulting code is correct and idiomatic and that `old_string` and `new_string` are different.
    5. NEVER escape `old_string` or `new_string`, that would break the exact literal text requirement.
    **Important:** If ANY of the above are not satisfied, the tool will fail. CRITICAL for `old_string`: Must uniquely identify the single instance to change. Include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely. If this string matches multiple locations, or does not match exactly, the tool will fail.
    6. Prefer to break down complex and long changes into multiple smaller atomic calls to this tool.
    **Multiple replacements:** If there are multiple and ambiguous occurences of the `old_string` in the file, the tool will also fail.

    Args:
        file_path: The path to the file to modify. Must be a file in the Editable files context.
        old_string: The exact literal text to replace, preferably unescaped. Include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely. If this string is not the exact literal text (i.e. you escaped it) or does not match exactly, the tool will fail.
        new_string: The exact literal text to replace `old_string` with, preferably unescaped. Provide the EXACT text. Ensure the resulting code is correct and idiomatic.

    """
    log.info(file_path)
    log.info(old_string)
    log.info(new_string)
    try:
        # Get file service to check if file is in editable context
        file_service = await make(FileService)

        # Convert to Path object for consistent handling
        file_path_obj = Path(file_path)

        # Check if file is in editable context
        file_context = file_service.get_file_context(file_path_obj)
        if file_context is None:
            log.info(
                f"Error: File '{file_path}' is not in the current context. Ask the user to add it first."
            )
            return f"Error: File '{file_path}' is not in the current context. Ask the user to add it first."

        if file_context.mode != FileMode.EDITABLE:
            log.info(
                f"Error: File '{file_path}' is not editable. It's currently {file_context.mode.value}."
            )
            return f"Error: File '{file_path}' is not editable. It's currently {file_context.mode.value}."

        # Use the absolute path from the context for file operations
        absolute_path = file_context.path

        if not absolute_path.exists():
            log.info(f"Error: File '{file_path}' does not exist")
            return f"Error: File '{file_path}' does not exist"

        if not absolute_path.is_file():
            log.info(f"Error: '{file_path}' is not a file")
            return f"Error: '{file_path}' is not a file"

        # Read current content
        original_content = absolute_path.read_text(encoding="utf-8")

        # Validate old_string and new_string are different
        if old_string == new_string:
            log.info("Error: old_string and new_string must be different")
            return "Error: old_string and new_string must be different"

        # Count occurrences to ensure single match
        match_count = original_content.count(old_string)
        if match_count == 0:
            log.info(
                f"Error: No matches found for the specified old_string in '{file_path}'"
            )
            return (
                f"Error: No matches found for the specified old_string in '{file_path}'"
            )
        elif match_count > 1:
            log.info(
                f"Error: Found {match_count} matches for old_string in '{file_path}'. The old_string must uniquely identify a single occurrence."
            )
            return f"Error: Found {match_count} matches for old_string in '{file_path}'. The old_string must uniquely identify a single occurrence."

        interaction_service = await make(InteractionService)
        console = await make(Console)

        # Show OLD TEXT in first panel
        console.print(
            Panel(
                old_string,
                title=f"[bold red]OLD TEXT - {file_path}[/bold red]",
                title_align="left",
                border_style="red",
            )
        )
        # Show NEW TEXT in second panel
        console.print(
            Panel(
                new_string,
                title=f"[bold green]NEW TEXT - {file_path}[/bold green]",
                title_align="left",
                border_style="blue",
            )
        )

        confirmed = await interaction_service.confirm(
            "Apply this change?", default=False
        )

        if not confirmed:
            # Ask user for explanation if they rejected the change
            reason = await interaction_service.input_text(
                "Why did you reject this change? (Press Enter to skip)", default=""
            )
            if reason.strip():
                return f"User rejected the change: {reason}"
            else:
                return "User rejected the change"

        # Perform the replacement
        new_content = original_content.replace(old_string, new_string, 1)

        # Write back to file
        absolute_path.write_text(new_content, encoding="utf-8")

        return f"Successfully replaced text in '{file_path}'. 1 occurrence replaced."

    except UnicodeDecodeError:
        return f"Error: Cannot read '{file_path}' - file contains non-UTF-8 content"
    except PermissionError:
        return f"Error: Permission denied writing to '{file_path}'"
    except Exception as e:
        return f"Error modifying '{file_path}': {e!s}"
