from pathlib import Path

from langchain.tools import ToolRuntime, tool

from byte.agent import AssistantContextSchema
from byte.files import FileContext, FileMode
from byte.prompt_format import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text


@tool(
    parse_docstring=True,
)
async def read_files(file_paths: list[str], runtime: ToolRuntime[AssistantContextSchema]) -> str:
    """Read the contents of a file from the project.

    This tool reads files that are available in the project's file discovery
    service, respecting gitignore patterns. It does require the file to
    be in the AI context.

    Args:
        file_paths: MUST BE A LIST, of file paths to read (relative to the project root)

    Returns:
        The contents of the file, or an error message if the file cannot be read
    """

    final_content = []

    for file_path in file_paths:
        # Check if file is in context first
        file_context = FileContext(path=Path(file_path), mode=FileMode.READ_ONLY)

        if file_context:
            content = file_context.get_content()

            language = file_context.language
            final_content.append(
                list_to_multiline_text(
                    [
                        Boundary.open(
                            BoundaryType.FILE,
                            meta={"source": file_context.relative_path, "language": language},
                        ),
                        f"```{language}",
                        f"{content}",
                        "```",
                        Boundary.close(BoundaryType.FILE),
                    ]
                )
            )

    return "\n\n".join(final_content)
