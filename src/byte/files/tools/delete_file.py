from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application
from byte.files import ToolFileService
from byte.tools import ToolResult


@tool(
    extras={"eager_input_streaming": True},
    description="Delete a file.",
)
async def delete_file(
    path: Annotated[str, "The EXACT Path to file located in `<file>`. Use the `source` variable."],
    app: Annotated[Application, InjectedToolArg],
) -> ToolResult:
    """Delete a file.

    Args:
        path: Absolute path to the file

    Returns:
        Success or error message
    """
    try:
        tool_file_service = app.make(ToolFileService)
        result = await tool_file_service.delete_file(path)

        return ToolResult(
            result=result,
            extra={
                "touched_files": [path],
            },
        )

    except Exception as e:
        return ToolResult(
            result=f"Error editing file: {e!s}",
        )
