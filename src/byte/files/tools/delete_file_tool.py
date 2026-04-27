from typing import Annotated, Any, Type, override

from langchain.tools import InjectedToolArg
from pydantic import BaseModel, Field

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult


class DeleteFileToolInput(BaseModel):
    """Input for DeleteFileTool"""

    file_path: str = Field(description="The EXACT Path to file located in `<file>`. Use the `source` variable.")
    app: Annotated[Any | None, InjectedToolArg]


class DeleteFileTool(BaseTool):
    name: str = "DeleteFileTool"
    description: str = "Delete a file."
    args_schema: Type[DeleteFileToolInput] = DeleteFileToolInput

    @override
    async def _arun(
        self,
        app: Application,
        file_path: str = "",
    ) -> ToolResult:

        try:
            tool_file_service = app.make(ToolFileService)
            result = await tool_file_service.delete_file(file_path)

            return ToolResult(
                result=result,
                extra={
                    "touched_files": [file_path],
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=f"Error editing file: {e!s}",
            )
