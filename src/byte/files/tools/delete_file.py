from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application


@tool(
    extras={"eager_input_streaming": True},
    description="Delete a file.",
)
def delete_file(
    path: Annotated[str, "Absolute path to the file to delete."],
    app: Annotated[Application, InjectedToolArg],
) -> str:
    """Delete a file.

    Args:
        path: Absolute path to the file

    Returns:
        Success or error message
    """
    try:
        full_path = app.path(path)

        if not full_path.exists():
            return f"Error: File '{path}' does not exist"

        if full_path.is_dir():
            return f"Error: '{path}' is a directory, not a file"

        full_path.unlink()
        return f"Successfully deleted '{path}'"

    except Exception as e:
        return f"Error deleting file: {e!s}"
