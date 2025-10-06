from typing import Optional

from langchain_core.tools import tool
from ripgrepy import Ripgrepy

from byte.context import make
from byte.core.config.config import ByteConfg


@tool(parse_docstring=True)
async def ripgrep_search(
    pattern: str,
    file_pattern: Optional[str] = None,
    case_sensitive: bool = False,
    max_results: Optional[int] = None,
) -> str:
    """Search for a pattern in the project using ripgrep.

    Args:
        pattern: The regex pattern to search for
        file_pattern: Optional glob pattern to filter files (e.g., "*.py")
        case_sensitive: Whether to perform case-sensitive search
        max_results: Maximum number of results to return

    Returns:
        String containing the search results with file paths and line numbers
    """
    config = await make(ByteConfg)
    project_root = str(config.project_root)

    # Initialize ripgrep with the pattern and project root
    rg = Ripgrepy(pattern, project_root)

    # Configure ripgrep options
    if not case_sensitive:
        rg = rg.ignore_case()

    if file_pattern:
        rg = rg.glob(file_pattern)

    if max_results:
        rg = rg.max_count(max_results)

    # Add line numbers and file paths for better context
    rg = rg.line_number().with_filename()

    # Execute the search
    try:
        result = rg.run()
        output = str(result)

        if not output or output.strip() == "":
            return f"No matches found for pattern: {pattern}"

        return output
    except Exception as e:
        return f"Error executing ripgrep search: {e!s}"
