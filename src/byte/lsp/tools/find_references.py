from pathlib import Path
from typing import List, override

from byte.lsp import Location, LSPService
from byte.tools import BaseTool, ToolResult


class FindReferencesTool(BaseTool):
    name: str = "find_references"
    description: str = "Find all references to a symbol at a specific position in a file. Uses the Language Server Protocol to find all locations where a symbol is referenced throughout the codebase."
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
            "include_declaration": {
                "type": "boolean",
                "description": "Whether to include the symbol's declaration in results",
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
        include_declaration: bool = False,
        **kwargs,
    ) -> ToolResult:
        lsp_service = self.app.make(LSPService)

        path_obj = Path(file_path).resolve()

        if not path_obj.exists():
            return ToolResult(result={"content": f"Error: File '{file_path}' does not exist"})

        try:
            locations: List[Location] = await lsp_service.find_references(path_obj, line, character)

            if not locations:
                return ToolResult(result={"content": f"No references found at {file_path}:{line}:{character}"})

            # Group references by file
            refs_by_file: dict[str, List[Location]] = {}
            for loc in locations:
                file_uri = loc.uri.removeprefix("file://")
                if file_uri not in refs_by_file:
                    refs_by_file[file_uri] = []
                refs_by_file[file_uri].append(loc)

            # Format results grouped by file
            results = []
            for file_uri in sorted(refs_by_file.keys()):
                file_refs = refs_by_file[file_uri]

                file_info = f"---\n\n{file_uri}\nReferences in File: {len(file_refs)}\n"

                loc_strings = []
                for ref in file_refs:
                    loc_str = f"L{ref.range.start.line + 1}:C{ref.range.start.character + 1}"
                    loc_strings.append(loc_str)

                if loc_strings:
                    file_info += "At: " + ", ".join(loc_strings) + "\n"

                try:
                    ref_path = Path(file_uri)
                    if ref_path.exists():
                        content = ref_path.read_text(encoding="utf-8")
                        lines = content.splitlines()

                        context_lines = 5
                        lines_to_show = set()

                        for ref in file_refs:
                            start_line = ref.range.start.line
                            for i in range(
                                max(0, start_line - context_lines), min(len(lines), start_line + context_lines + 1)
                            ):
                                lines_to_show.add(i)

                        sorted_lines = sorted(lines_to_show)
                        line_ranges = []
                        if sorted_lines:
                            range_start = sorted_lines[0]
                            range_end = sorted_lines[0]

                            for line_num in sorted_lines[1:]:
                                if line_num == range_end + 1:
                                    range_end = line_num
                                else:
                                    line_ranges.append((range_start, range_end))
                                    range_start = line_num
                                    range_end = line_num
                            line_ranges.append((range_start, range_end))

                        formatted_lines = []
                        for range_start, range_end in line_ranges:
                            if formatted_lines:
                                formatted_lines.append("...")

                            for i in range(range_start, range_end + 1):
                                if i < len(lines):
                                    formatted_lines.append(f"{i + 1:4d} | {lines[i]}")

                        file_info += "\n" + "\n".join(formatted_lines)
                        results.append(file_info)
                    else:
                        results.append(file_info + "\nError: File not found locally")
                except Exception as e:
                    results.append(file_info + f"\nError reading file: {e!s}")

            return ToolResult(result={"content": "\n".join(results)})

        except Exception as e:
            return ToolResult(result={"content": f"Error finding references: {e!s}"})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
