from pathlib import Path

from langchain_core.tools import tool

from byte.context import make
from byte.domain.lsp.service.lsp_service import LSPService


@tool(parse_docstring=True)
async def get_hover_info(file_path: str, line: int, character: int) -> str:
    """Get hover information for a symbol at a specific position in a file.

    This tool uses the Language Server Protocol to retrieve documentation,
    type information, and other details about code symbols when you hover
    over them in an editor.

    Args:
            file_path: The path to the file (relative or absolute)
            line: The line number (one-based, as shown in editors)
            character: The character position on the line (zero-based)

    Returns:
            Hover information as a string, or an error message if unavailable
    """
    lsp_service = await make(LSPService)

    # Convert string path to Path object
    path_obj = Path(file_path).resolve()

    # Check if file exists
    if not path_obj.exists():
        return f"Error: File '{file_path}' does not exist"

    # Get hover information
    try:
        hover_result = await lsp_service.get_hover(path_obj, line, character)

        if hover_result:
            return hover_result.contents
        else:
            return f"No hover information available at {file_path}:{line}:{character}"

    except Exception as e:
        return f"Error getting hover information: {e!s}"
