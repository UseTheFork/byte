from pathlib import Path

from langchain_core.tools import tool


@tool(parse_docstring=True)
async def replace_text_in_file(
    file_path: str,
    old_string: str,
    new_string: str,
) -> str:
    """Replaces text within a file. Replaces a single occurrence. This tool requires providing significant context around the change to ensure precise targeting.

    The user has the ability to modify the `new_string` content. If modified, this will be stated in the response.

    Expectation for required parameters:
    1. `file_path` MUST be an absolute path; otherwise an error will be thrown.
    2. `old_string` MUST be the exact literal text to replace (including all whitespace, indentation, newlines, and surrounding code etc.).
    3. `new_string` MUST be the exact literal text to replace `old_string` with (also including all whitespace, indentation, newlines, and surrounding code etc.). Ensure the resulting code is correct and idiomatic and that `old_string` and `new_string` are different.
    5. NEVER escape `old_string` or `new_string`, that would break the exact literal text requirement.
    **Important:** If ANY of the above are not satisfied, the tool will fail. CRITICAL for `old_string`: Must uniquely identify the single instance to change. Include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely. If this string matches multiple locations, or does not match exactly, the tool will fail.
    6. Prefer to break down complex and long changes into multiple smaller atomic calls to this tool.
    **Multiple replacements:** If there are multiple and ambiguous occurences of the `old_string` in the file, the tool will also fail.

    Args:
        file_path: The absolute path to the file to modify. Must start with '/'.
        old_string: The exact literal text to replace, preferably unescaped. Include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely. If this string is not the exact literal text (i.e. you escaped it) or does not match exactly, the tool will fail.
        new_string: The exact literal text to replace `old_string` with, preferably unescaped. Provide the EXACT text. Ensure the resulting code is correct and idiomatic.

    """
    try:
        # Validate file path is absolute
        if not file_path.startswith("/"):
            return f"Error: File path '{file_path}' must be absolute (start with '/')"

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return f"Error: File '{file_path}' does not exist"

        if not file_path_obj.is_file():
            return f"Error: '{file_path}' is not a file"

        # Read current content
        original_content = file_path_obj.read_text(encoding="utf-8")

        # Validate old_string and new_string are different
        if old_string == new_string:
            return "Error: old_string and new_string must be different"

        # Count occurrences to ensure single match
        match_count = original_content.count(old_string)
        if match_count == 0:
            return (
                f"Error: No matches found for the specified old_string in '{file_path}'"
            )
        elif match_count > 1:
            return f"Error: Found {match_count} matches for old_string in '{file_path}'. The old_string must uniquely identify a single occurrence."

        # Perform the replacement
        new_content = original_content.replace(old_string, new_string, 1)

        # Write back to file
        file_path_obj.write_text(new_content, encoding="utf-8")

        return f"Successfully replaced text in '{file_path}'. 1 occurrence replaced."

    except UnicodeDecodeError:
        return f"Error: Cannot read '{file_path}' - file contains non-UTF-8 content"
    except PermissionError:
        return f"Error: Permission denied writing to '{file_path}'"
    except Exception as e:
        return f"Error modifying '{file_path}': {e!s}"
