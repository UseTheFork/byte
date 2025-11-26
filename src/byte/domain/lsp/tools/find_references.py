from pathlib import Path
from typing import List

from langchain_core.tools import tool

from byte.context import make
from byte.domain.lsp.schemas import Location
from byte.domain.lsp.service.lsp_service import LSPService


@tool(parse_docstring=True)
async def find_references(file_path: str, line: int, character: int, include_declaration: bool = False) -> str:
    """Find all references to a symbol at a specific position in a file.

    This tool uses the Language Server Protocol to find all locations where
    a symbol is referenced throughout the codebase. It can optionally include
    the declaration location as well.

    Args:
            file_path: The path to the file (relative or absolute)
            line: The line number (zero-based)
            character: The character position on the line (zero-based)
            include_declaration: Whether to include the symbol's declaration in results

    Returns:
            Reference information grouped by file with context, or an error message if unavailable
    """
    lsp_service = await make(LSPService)

    # Convert string path to Path object
    path_obj = Path(file_path).resolve()

    # Check if file exists
    if not path_obj.exists():
        return f"Error: File '{file_path}' does not exist"

    # Get reference locations
    try:
        locations: List[Location] = await lsp_service.find_references(path_obj, line, character)

        if not locations:
            return f"No references found at {file_path}:{line}:{character}"

        # Group references by file
        refs_by_file: dict[str, List[Location]] = {}
        for loc in locations:
            file_uri = loc.uri.removeprefix("file://")
            if file_uri not in refs_by_file:
                refs_by_file[file_uri] = []
            refs_by_file[file_uri].append(loc)

        # Format results grouped by file
        results = []
        for file_uri in sorted(refs_by_file.keys()):
            file_refs = refs_by_file[file_uri]

            # Format file header
            file_info = f"---\n\n{file_uri}\nReferences in File: {len(file_refs)}\n"

            # Collect location strings for header
            loc_strings = []
            for ref in file_refs:
                loc_str = f"L{ref.range.start.line + 1}:C{ref.range.start.character + 1}"
                loc_strings.append(loc_str)

            if loc_strings:
                file_info += "At: " + ", ".join(loc_strings) + "\n"

            # Read file content to show context
            try:
                ref_path = Path(file_uri)
                if ref_path.exists():
                    content = ref_path.read_text(encoding="utf-8")
                    lines = content.splitlines()

                    # Collect all lines to display with context
                    context_lines = 5
                    lines_to_show = set()

                    for ref in file_refs:
                        start_line = ref.range.start.line
                        # Add context around each reference
                        for i in range(
                            max(0, start_line - context_lines), min(len(lines), start_line + context_lines + 1)
                        ):
                            lines_to_show.add(i)

                    # Convert to sorted list and create ranges
                    sorted_lines = sorted(lines_to_show)
                    line_ranges = []
                    if sorted_lines:
                        range_start = sorted_lines[0]
                        range_end = sorted_lines[0]

                        for line_num in sorted_lines[1:]:
                            if line_num == range_end + 1:
                                range_end = line_num
                            else:
                                line_ranges.append((range_start, range_end))
                                range_start = line_num
                                range_end = line_num
                        line_ranges.append((range_start, range_end))

                    # Format the content with ranges
                    formatted_lines = []
                    for range_start, range_end in line_ranges:
                        if formatted_lines:
                            formatted_lines.append("...")

                        for i in range(range_start, range_end + 1):
                            if i < len(lines):
                                formatted_lines.append(f"{i + 1:4d} | {lines[i]}")

                    file_info += "\n" + "\n".join(formatted_lines)
                    results.append(file_info)
                else:
                    # File doesn't exist locally
                    results.append(file_info + "\nError: File not found locally")
            except Exception as e:
                results.append(file_info + f"\nError reading file: {e!s}")

        return "\n".join(results)

    except Exception as e:
        return f"Error finding references: {e!s}"
