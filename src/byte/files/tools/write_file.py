from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application


@tool(
    extras={"eager_input_streaming": True},
    description="Write content to a file. Creates parent directories if needed.",
)
def write_file(
    path: Annotated[str, "Absolute path to the file (e.g., /main.py, /src/utils.py)"],
    content: Annotated[str, "Content to write to the file"],
    app: Annotated[Application, InjectedToolArg],
) -> str:
    """Write content to a file. Creates parent directories if needed.

    Args:
        path: Absolute path to the file
        content: Content to write

    Returns:
        Success or error message
    """
    try:
        full_path = app.path(path)

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        full_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to '{path}'"

    except Exception as e:
        return f"Error writing file: {e!s}"
