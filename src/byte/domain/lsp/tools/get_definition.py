from pathlib import Path
from typing import List

from langchain_core.tools import tool

from byte.context import make
from byte.domain.lsp.schemas import Location
from byte.domain.lsp.service.lsp_service import LSPService


@tool(parse_docstring=True)
async def get_definition(file_path: str, line: int, character: int) -> str:
    """Get the definition location(s) for a symbol at a specific position in a file.

    This tool uses the Language Server Protocol to find where a symbol is defined.
    It can return multiple locations if the symbol has multiple definitions.

    Args:
            file_path: The path to the file (relative or absolute)
            line: The line number (one-based, as shown in editors)
            character: The character position on the line (zero-based)

    Returns:
            Definition information with file paths and ranges, or an error message if unavailable
    """
    lsp_service = await make(LSPService)

    # Convert string path to Path object
    path_obj = Path(file_path).resolve()

    # Check if file exists
    if not path_obj.exists():
        return f"Error: File '{file_path}' does not exist"

    # Get definition locations
    try:
        locations: List[Location] = await lsp_service.goto_definition(path_obj, line, character)

        if not locations:
            return f"No definition found at {file_path}:{line}:{character}"

        # Format results similar to the Go example
        results = []
        for loc in locations:
            # Extract file path from URI
            file_uri = loc.uri
            file_uri = file_uri.removeprefix("file://")  # Remove 'file://' prefix

            # Read the file content to show the definition
            try:
                definition_path = Path(file_uri)
                if definition_path.exists():
                    content = definition_path.read_text(encoding="utf-8")
                    lines = content.splitlines()

                    # Extract the relevant lines for the definition
                    start_line = loc.range.start.line
                    end_line = loc.range.end.line

                    # Get a few lines of context
                    context_start = max(0, start_line - 2)
                    context_end = min(len(lines), end_line + 3)
                    definition_lines = lines[context_start:context_end]

                    # Add line numbers
                    numbered_lines = []
                    for i, line_content in enumerate(definition_lines, start=context_start + 1):
                        numbered_lines.append(f"{i:4d} | {line_content}")

                    definition_text = "\n".join(numbered_lines)

                    result = (
                        f"---\n\n"
                        f"File: {file_uri}\n"
                        f"Range: L{start_line + 1}:C{loc.range.start.character + 1} - "
                        f"L{end_line + 1}:C{loc.range.end.character + 1}\n\n"
                        f"{definition_text}\n"
                    )
                    results.append(result)
                else:
                    # File doesn't exist locally, just show location
                    result = (
                        f"---\n\n"
                        f"File: {file_uri}\n"
                        f"Range: L{start_line + 1}:C{loc.range.start.character + 1} - "
                        f"L{end_line + 1}:C{loc.range.end.character + 1}\n"
                    )
                    results.append(result)
            except Exception as e:
                # If we can't read the file, just show the location
                result = (
                    f"---\n\n"
                    f"File: {file_uri}\n"
                    f"Range: L{loc.range.start.line + 1}:C{loc.range.start.character + 1} - "
                    f"L{loc.range.end.line + 1}:C{loc.range.end.character + 1}\n"
                    f"Error reading file: {e!s}\n"
                )
                results.append(result)

        return "\n".join(results)

    except Exception as e:
        return f"Error getting definition: {e!s}"
