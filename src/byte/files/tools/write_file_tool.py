from typing import Annotated, Any, override

from langchain.tools import InjectedToolArg
from langchain_core.tools import ArgsSchema
from pydantic import BaseModel, Field

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult


class WriteFileToolInput(BaseModel):
    """Input for WriteFileTool"""

    path: Annotated[
        str,
        Field(description="The EXACT Path to the file."),
    ]
    content: Annotated[
        str,
        Field(description="Content to write to the file."),
    ]
    app: Annotated[Any | None, InjectedToolArg]


class WriteFileTool(BaseTool):
    name: str = "WriteFileTool"
    description: str = "Write content to a file. Creates parent directories if needed."
    args_schema: ArgsSchema | None = WriteFileToolInput

    @override
    async def _arun(
        self,
        app: Application,
        path: str = "",
        content: str = "",
    ) -> ToolResult:

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
