from typing import override

from byte.files import FileContext, FileMode
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult


class ReadFilesTool(BaseTool):
    name: str = "read_files"
    description: str = "Read the contents of one or more files from the project."
    input_schema = {
        "type": "object",
        "properties": {
            "file_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths to read (relative to the project root)",
            },
        },
        "required": ["file_paths"],
    }

    @override
    async def run(
        self,
        file_paths: list[str] = [],
    ) -> ToolResult:

        final_content = []

        for file_path in file_paths:
            file_context = FileContext(
                path=self.app.path(file_path),
                mode=FileMode.READ_ONLY,
                root_path=self.app.path(),
            )

            content = file_context.get_content()
            if content is not None:
                language = file_context.language
                final_content.append(
                    list_to_multiline_text(
                        [
                            Boundary.open(
                                BoundaryType.FILE,
                                meta={"source": file_context.relative_path, "language": language},
                            ),
                            f"{content}",
                            Boundary.close(BoundaryType.FILE),
                        ]
                    )
                )

        return ToolResult(result="\n\n".join(final_content))
