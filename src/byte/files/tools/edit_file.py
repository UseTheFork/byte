from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application
from byte.files import ToolFileService
from byte.tools import ToolResult

# SINGLE INSTANCE: Tool changes ONE instance when replace_all=false

# - For multiple instances: set replace_all=true OR make separate calls with unique context
# UNIQUENESS (when replace_all=false): old_string MUST uniquely identify target instance


@tool(
    extras={"eager_input_streaming": True},
    description="""Edit a file by replacing a specific string. The old_string must match exactly character for character.
    
<critical_requirements>
EXACT MATCHING: The tool is extremely literal. Text must match **EXACTLY**

- Every space and tab character
- Every blank line
- Every newline character
- Indentation level (count the spaces/tabs)
- Comment spacing (`// comment` vs `//comment`)
- Brace positioning (`func() {` vs `func(){`)

Common failures:

```
Expected: "    func foo() {"     (4 spaces)
Provided: "  func foo() {"       (2 spaces) ❌ FAILS

Expected: "}\n\nfunc bar() {"    (2 newlines)
Provided: "}\nfunc bar() {"      (1 newline) ❌ FAILS

Expected: "// Comment"           (space after //)
Provided: "//Comment"            (no space) ❌ FAILS
```

UNIQUENESS: old_string MUST uniquely identify target instance

- Include 3-5 lines context BEFORE and AFTER change point
- Include exact whitespace, indentation, surrounding code
- If text appears multiple times, add more context to make it unique


- Plan calls carefully to avoid conflicts
</critical_requirements>
<warnings>
Tool fails if:
- old_string matches multiple locations
- old_string doesn't match exactly (including whitespace)
- Insufficient context causes wrong instance change
- Indentation is off by even one space
- Missing or extra blank lines
- Wrong tabs vs spaces
</warnings>""",
)
async def edit_file(
    path: Annotated[str, "The EXACT Path to a `editable` file located in `<file>`. Use the `source` variable."],
    old_string: Annotated[str, "The exact string to find and replace"],
    new_string: Annotated[str, "The string to replace with"],
    app: Annotated[Application, InjectedToolArg],
) -> ToolResult:
    """Edit a file by replacing a specific string. The old_string must match exactly.

    Args:
        path: Absolute path to the file
        old_string: Exact string to find (must be unique in file)
        new_string: String to replace with

    Returns:
        Success or error message
    """
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
