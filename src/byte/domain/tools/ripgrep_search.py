import shutil
import subprocess
from typing import Optional

from langchain_core.tools import tool

from byte.context import make
from byte.core.config.config import ByteConfg


def _check_ripgrep_installed() -> bool:
    """Check if ripgrep is installed on the system.

    Usage: `if _check_ripgrep_installed(): ...`
    """
    return shutil.which("rg") is not None


@tool(parse_docstring=True)
async def ripgrep_search(
    pattern: str,
    file_pattern: Optional[str] = None,
    case_sensitive: bool = False,
    max_results: Optional[int] = None,
) -> str:
    """Search for a pattern in the project using ripgrep.

    Args:
            pattern: The regex pattern to search for
            file_pattern: Optional glob pattern to filter files (e.g., "*.py")
            case_sensitive: Whether to perform case-sensitive search
            max_results: Maximum number of results to return

    Returns:
            String containing the search results with file paths and line numbers
    """
    # Check if ripgrep is installed
    if not _check_ripgrep_installed():
        return "Error: ripgrep (rg) is not installed. Please install it to use this feature."

    config = await make(ByteConfg)
    project_root = str(config.project_root)

    # Build ripgrep command
    cmd = ["rg", pattern, project_root, "--line-number", "--with-filename"]

    # Configure ripgrep options
    if not case_sensitive:
        cmd.append("--ignore-case")

    if file_pattern:
        cmd.extend(["--glob", file_pattern])

    if max_results:
        cmd.extend(["--max-count", str(max_results)])

    # Execute the search
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=project_root)

        # ripgrep returns exit code 1 when no matches found (not an error)
        if result.returncode == 0:
            return result.stdout if result.stdout else f"No matches found for pattern: {pattern}"
        elif result.returncode == 1:
            return f"No matches found for pattern: {pattern}"
        else:
            # Actual error occurred
            return f"Error executing ripgrep search: {result.stderr}"

    except subprocess.SubprocessError as e:
        return f"Error executing ripgrep search: {e!s}"
