from typing import Annotated, Any, Type, override

from langchain.tools import InjectedToolArg
from pydantic import BaseModel, Field

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult


class WriteFileToolInput(BaseModel):
    """Input for WriteFileTool"""

    file_path: str = Field(description="The EXACT Path to the file.")
    content: str = Field(description="Content to write to the file.")
    app: Annotated[Any | None, InjectedToolArg]


class WriteFileTool(BaseTool):
    name: str = "WriteFileTool"
    description: str = "Write content to a file. Creates parent directories if needed."
    args_schema: Type[WriteFileToolInput] = WriteFileToolInput

    @override
    async def _arun(
        self,
        app: Application,
        file_path: str = "",
        content: str = "",
    ) -> ToolResult:

        try:
            tool_file_service = app.make(ToolFileService)
            result = await tool_file_service.write_file(file_path, content)

            return ToolResult(
                result=result,
                extra={
                    "touched_files": [file_path],
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=f"Error writing file: {e!s}",
            )
