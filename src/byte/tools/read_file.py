from pathlib import Path

from langchain_core.tools import tool

from byte.context import make
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService


@tool(parse_docstring=True)
async def read_file(file_path: str) -> str:
    """Read the contents of a file from the project.

    This tool reads files that are available in the project's file discovery
    service, respecting gitignore patterns. It does not require the file to
    be in the AI context.

    Args:
            file_path: The path to the file to read (relative or absolute)

    Returns:
            The contents of the file, or an error message if the file cannot be read
    """
    file_service = await make(FileService)

    # Check if file is in context first
    file_context = file_service.get_file_context(file_path)
    if file_context:
        content = file_context.get_content()
        if content is not None:
            return content
        return f"Error: File '{file_path}' is in context but could not be read"

    discovery_service = await make(FileDiscoveryService)
    discovered_files = await discovery_service.get_files()
    discovered_file_paths = {str(f.resolve()) for f in discovered_files}

    # Resolve the path
    path_obj = Path(file_path).resolve()

    # Check if file is in discovery service
    if str(path_obj) not in discovered_file_paths:
        return f"Error: File '{file_path}' not found in project or is ignored by gitignore"

    # Read the file directly
    try:
        content = path_obj.read_text(encoding="utf-8")
        return content
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        return f"Error reading file '{file_path}': {e!s}"
