from typing import Annotated, Any, override

from langchain.tools import InjectedToolArg
from langchain_core.tools import ArgsSchema
from pydantic import BaseModel, Field

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult


class ReplaceFileToolInput(BaseModel):
    """Input for ReplaceFileTool"""

    path: Annotated[
        str,
        Field(description="The EXACT Path to file located in `<file>`. Use the `source` variable."),
    ]
    content: Annotated[
        str,
        Field(description="Content to replace the file with"),
    ]
    app: Annotated[Any | None, InjectedToolArg]


class ReplaceFileTool(BaseTool):
    name: str = "ReplaceFileTool"
    description: str = "Replace all content in a file."
    args_schema: ArgsSchema | None = ReplaceFileToolInput

    @override
    async def _arun(
        self,
        app: Application,
        path: str = "",
        content: str = "",
    ) -> ToolResult:

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
                success=False,
                result=f"Error replacing file: {e!s}",
            )
