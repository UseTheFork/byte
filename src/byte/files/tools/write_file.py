from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application
from byte.files import ToolFileService
from byte.tools import ToolResult


@tool(
    extras={"eager_input_streaming": True},
    description="Write content to a file. Creates parent directories if needed.",
)
async def write_file(
    path: Annotated[str, "The EXACT Path to the file located in `<file>`. Use the `source` variable."],
    content: Annotated[str, "Content to write to the file"],
    app: Annotated[Application, InjectedToolArg],
) -> ToolResult:
    """Write content to a file. Creates parent directories if needed.

    Args:
        path: Absolute path to the file
        content: Content to write

    Returns:
        Success or error message
    """
    try:
        tool_file_service = app.make(ToolFileService)
        result = await tool_file_service.write_file(path, content)

        return ToolResult(
            result=result,
            extra={
                "touched_files": [path],
            },
        )

    except Exception as e:
        return ToolResult(
            result=f"Error writing file: {e!s}",
        )
