from pathlib import Path
from typing import List, override

from byte.lsp import Location, LSPService
from byte.tools import BaseTool, ToolResult


class GetDefinitionTool(BaseTool):
    name: str = "get_definition"
    description: str = "Get the definition location(s) for a symbol at a specific position in a file. Uses the Language Server Protocol to find where a symbol is defined."
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file (relative or absolute)",
            },
            "line": {
                "type": "integer",
                "description": "The line number (one-based, as shown in editors)",
            },
            "character": {
                "type": "integer",
                "description": "The character position on the line (zero-based)",
            },
        },
        "required": ["file_path", "line", "character"],
    }

    @override
    async def run(
        self,
        file_path: str = "",
        line: int = 0,
        character: int = 0,
        **kwargs,
    ) -> ToolResult:
        lsp_service = self.app.make(LSPService)

        path_obj = Path(file_path).resolve()

        if not path_obj.exists():
            return ToolResult(result={"content": f"Error: File '{file_path}' does not exist"})

        try:
            locations: List[Location] = await lsp_service.goto_definition(path_obj, line, character)

            if not locations:
                return ToolResult(result={"content": f"No definition found at {file_path}:{line}:{character}"})

            results = []
            for loc in locations:
                file_uri = loc.uri.removeprefix("file://")

                try:
                    definition_path = Path(file_uri)
                    if definition_path.exists():
                        content = definition_path.read_text(encoding="utf-8")
                        lines = content.splitlines()

                        start_line = loc.range.start.line
                        end_line = loc.range.end.line

                        context_start = max(0, start_line - 2)
                        context_end = min(len(lines), end_line + 3)
                        definition_lines = lines[context_start:context_end]

                        numbered_lines = []
                        for i, line_content in enumerate(definition_lines, start=context_start + 1):
                            numbered_lines.append(f"{i:4d} | {line_content}")

                        definition_text = "\n".join(numbered_lines)

                        result = (
                            f"---\n\n"
                            f"File: {file_uri}\n"
                            f"Range: L{start_line + 1}:C{loc.range.start.character + 1} - "
                            f"L{end_line + 1}:C{loc.range.end.character + 1}\n\n"
                            f"{definition_text}\n"
                        )
                        results.append(result)
                    else:
                        start_line = loc.range.start.line
                        end_line = loc.range.end.line
                        result = (
                            f"---\n\n"
                            f"File: {file_uri}\n"
                            f"Range: L{start_line + 1}:C{loc.range.start.character + 1} - "
                            f"L{end_line + 1}:C{loc.range.end.character + 1}\n"
                        )
                        results.append(result)
                except Exception as e:
                    result = (
                        f"---\n\n"
                        f"File: {file_uri}\n"
                        f"Range: L{loc.range.start.line + 1}:C{loc.range.start.character + 1} - "
                        f"L{loc.range.end.line + 1}:C{loc.range.end.character + 1}\n"
                        f"Error reading file: {e!s}\n"
                    )
                    results.append(result)

            return ToolResult(result={"content": "\n".join(results)})

        except Exception as e:
            return ToolResult(result={"content": f"Error getting definition: {e!s}"})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
