from typing import Annotated, Any, override

from langchain.tools import InjectedToolArg
from langchain_core.tools import ArgsSchema
from pydantic import BaseModel, Field

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult


class EditFileToolInput(BaseModel):
    """Input for EditFileTool"""

    file_path: str = Field(
        description="The EXACT Path to a `editable` file located in `<file>`. Use the `source` variable."
    )
    search_string: str = Field(
        description="The EXACT string to search for. UNIQUENESS: search_string MUST uniquely identify target instance. Include 3-5 lines context BEFORE and AFTER change point, Include exact whitespace, indentation, surrounding code, If text appears multiple times, add more context to make it unique."
    )
    replace_string: str = Field(description="The string to replace the `search_string` with.")
    app: Annotated[Any | None, InjectedToolArg]


class EditFileTool(BaseTool):
    name: str = "EditFileTool"
    description: str = """Edit a file by replacing a specific string. The search_string must match exactly character for character.\n\n > **Critical **: The tool is extremely literal. Text must match **EXACTLY**"""
    args_schema: ArgsSchema = EditFileToolInput

    @override
    async def _arun(
        self,
        app: Application,
        file_path: str = "",
        search_string: str = "",
        replace_string: str = "",
    ) -> ToolResult:

        try:
            tool_file_service = app.make(ToolFileService)

            result = await tool_file_service.edit_file(file_path, search_string, replace_string)

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
