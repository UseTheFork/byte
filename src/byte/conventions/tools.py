from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application
from byte.parsing import ConventionParsingService


@tool(parse_docstring=True)
async def load_convention(
    convention_name: str,
    app: Annotated[Application | None, InjectedToolArg] = None,
) -> str:
    """Load a convention file by its name.

    This tool reads convention files using the name from convention metadata.

    Args:
            convention_name: The name of the convention (from <name>)

    Returns:
            The contents of the convention, or an error message if the convention cannot be read
    """
    if app is None:
        raise RuntimeError("Application instance is required but was not provided")

    convention_parsing_service = app.make(ConventionParsingService)
    file_path = app.conventions_path(f"{convention_name}.md")

    try:
        content = convention_parsing_service.read_content(file_path)
        return content
    except Exception as e:
        return f"Error loading convention file '{file_path}': {e!s}"
