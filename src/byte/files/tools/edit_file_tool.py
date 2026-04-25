from typing import Annotated, Any, override

from langchain.tools import InjectedToolArg
from langchain_core.tools import ArgsSchema
from pydantic import BaseModel, Field

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult


class EditFileToolInput(BaseModel):
    """Input for EditFileTool"""

    old_string: Annotated[
        str,
        Field(description="The EXACT string to find and replace"),
    ]
    new_string: Annotated[
        str,
        Field(description="The string to replace with."),
    ]
    path: Annotated[
        str,
        Field(description="The EXACT Path to a `editable` file located in `<file>`. Use the `source` variable."),
    ]
    app: Annotated[Any | None, InjectedToolArg]


class EditFileTool(BaseTool):
    name: str = "EditFileTool"
    description: str = """Edit a file by replacing a specific string. The old_string must match exactly character for character.
    
<critical_requirements>
EXACT MATCHING: The tool is extremely literal. Text must match **EXACTLY**

- Every space and tab character
- Every blank line
- Every newline character
- Indentation level (count the spaces/tabs)
- Comment spacing (`// comment` vs `//comment`)
- Brace positioning (`func() {` vs `func(){`)

UNIQUENESS: old_string MUST uniquely identify target instance

- Include 3-5 lines context BEFORE and AFTER change point
- Include exact whitespace, indentation, surrounding code
- If text appears multiple times, add more context to make it unique

</critical_requirements>"""
    args_schema: ArgsSchema | None = EditFileToolInput

    @override
    async def _arun(
        self,
        app: Application,
        path: str = "",
        old_string: str = "",
        new_string: str = "",
    ) -> ToolResult:

        try:
            tool_file_service = app.make(ToolFileService)

            result = await tool_file_service.edit_file(path, old_string, new_string)

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
