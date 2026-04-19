from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application
from byte.files import ToolFileService
from byte.tools import ToolResult


@tool(
    extras={"eager_input_streaming": True},
    description="Replace all content in a file.",
)
async def replace_file(
    path: Annotated[str, "The EXACT Path to file located in `<file>`. Use the `source` variable."],
    content: Annotated[str, "Content to replace the file with"],
    app: Annotated[Application, InjectedToolArg],
) -> ToolResult:
    """Replace all content in a file.

    Args:
        path: Absolute path to the file
        content: Content to replace the file with

    Returns:
        Success or error message
    """
    try:
        tool_file_service = app.make(ToolFileService)
        result = await tool_file_service.replace_file(path, content)

        return ToolResult(
            result=result,
            extra={
                "touched_files": [path],
            },
        )

    except Exception as e:
        return ToolResult(
            result=f"Error replacing file: {e!s}",
        )
