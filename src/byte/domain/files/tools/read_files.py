from pathlib import Path

from langchain_core.tools import tool

from byte.context import make
from byte.domain.files.service.file_service import FileService


@tool(
    parse_docstring=True,
)
async def read_files(file_paths: list[str]) -> str:
    """Read the contents of a file from the project.

    This tool reads files that are available in the project's file discovery
    service, respecting gitignore patterns. It does require the file to
    be in the AI context.

    Args:
        file_paths: MUST BE A LIST, of file paths to read (relative to the project root)

    Returns:
        The contents of the file, or an error message if the file cannot be read
    """
    file_service = await make(FileService)

    final_content = []

    for file_path in file_paths:
        # Check if file is in context first
        file_context = file_service.get_file_context(file_path)
        if file_context:
            content = file_context.get_content()
            if content is not None:
                language = file_context.language
                final_content.append(
                    f"<file: source={file_context.relative_path}, language={language}>\n{content}\n</file>"
                )
                continue
            final_content.append(f"Error: File '{file_path}' is in context but could not be read")
            continue

        # Resolve the path
        path_obj = Path(file_path).resolve()

        # Read the file directly
        try:
            content = path_obj.read_text(encoding="utf-8")
            # Determine language from file extension
            language = path_obj.suffix.lstrip(".") if path_obj.suffix else "text"
            final_content.append(f"<file: source={file_path}, language={language}>\n{content}\n</file>")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            final_content.append(f"Error reading file '{file_path}': {e!s}")

    return "\n\n".join(final_content)
