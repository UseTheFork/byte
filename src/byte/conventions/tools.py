from langchain_core.tools import tool

from byte.context import make
from byte.parsing import SkillParsingService


@tool(parse_docstring=True)
async def load_conventions(file_path: str) -> str:
    """Load a convention file by its location path.

    This tool reads convention files using the location from convention metadata.

    Args:
            file_path: The path to the convention file (from convention_props.location)

    Returns:
            The contents of the convention file, or an error message if the file cannot be read
    """
    skill_parsing_service = make(SkillParsingService)

    try:
        content = skill_parsing_service.read_skill_content(file_path)
        return content
    except Exception as e:
        return f"Error loading convention file '{file_path}': {e!s}"
