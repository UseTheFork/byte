from typing import TYPE_CHECKING, List

from rich.console import Console

from byte.context import make
from byte.core.command.registry import Command
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service import FileService

if TYPE_CHECKING:
    from rich.console import Console


class AddFileCommand(Command):
    """Command to add files to AI context as editable.

    Enables users to make files available for AI modification via
    SEARCH/REPLACE blocks, with intelligent tab completion from project files.
    Usage: `/add main.py` -> file becomes editable in AI context
    """

    @property
    def name(self) -> str:
        return "add"

    @property
    def description(self) -> str:
        return "Add file to context as editable"

    async def execute(self, args: str) -> None:
        """Add specified file to context with editable permissions."""
        console = await make(Console)

        if not args:
            console.print("Usage: /add <file_path>")
            return

        file_service = await make(FileService)
        if await file_service.add_file(args, FileMode.EDITABLE):
            console.print(f"[success]Added {args} to context as editable[/success]")
            return
        else:
            console.print(
                f"[error]Failed to add {args} (file not found or not readable)[/error]"
            )
            return

    async def get_completions(self, text: str) -> List[str]:
        """Provide intelligent file path completions from project discovery.

        Uses the file discovery service to suggest project files that match
        the input pattern, respecting gitignore patterns automatically.
        """
        try:
            file_service = await make(FileService)

            # Get project files matching the pattern
            matches = await file_service.find_project_files(text)

            # Filter out files already in context to avoid duplicates
            return [f for f in matches if not await file_service.is_file_in_context(f)]
        except Exception:
            # Fallback to empty list if discovery fails
            return []


class ReadOnlyCommand(Command):
    """Command to add files to AI context as read-only references.

    Allows AI to reference file content for context without permission
    to modify, useful for configuration files, documentation, or examples.
    Usage: `/read-only config.json` -> file available for reference only
    """

    @property
    def name(self) -> str:
        return "read-only"

    @property
    def description(self) -> str:
        return "Add file to context as read-only"

    async def execute(self, args: str) -> None:
        """Add specified file to context with read-only permissions."""
        console = await make(Console)
        if not args:
            console.print("Usage: /read-only <file_path>")
            return

        file_service = await make(FileService)
        if await file_service.add_file(args, FileMode.READ_ONLY):
            console.print(f"[success]Added {args} to context as read-only[/success]")
            return
        else:
            console.print(
                f"[error]Failed to add {args} (file not found or not readable)[/error]"
            )
            return

    async def get_completions(self, text: str) -> List[str]:
        """Provide intelligent file path completions from project discovery.

        Uses the same completion logic as AddFileCommand for consistency,
        suggesting project files that match the input pattern.
        """
        try:
            file_service = await make(FileService)

            matches = await file_service.find_project_files(text)
            return [f for f in matches if not await file_service.is_file_in_context(f)]
        except Exception:
            return []


class DropFileCommand(Command):
    """Command to remove files from AI context.

    Enables users to clean up context by removing files that are no
    longer relevant, reducing noise and improving AI focus on current task.
    Usage: `/drop old_file.py` -> removes file from AI awareness
    """

    def __init__(self, container=None):
        self.container = container

    @property
    def name(self) -> str:
        return "drop"

    @property
    def description(self) -> str:
        return "Remove file from context"

    async def execute(self, args: str) -> None:
        """Remove specified file from active context."""
        console = await make(Console)
        if not args:
            console.print("Usage: /drop <file_path>")
            return

        file_service: FileService = await make(FileService)
        if await file_service.remove_file(args):
            console.print(f"[success]Removed {args} from context[/success]")
            return
        else:
            console.print(f"[error]File {args} not found in context[/error]")
            return

    async def get_completions(self, text: str) -> List[str]:
        """Provide intelligent file path completions from project discovery.

        Uses the same completion logic as AddFileCommand for consistency,
        suggesting project files that match the input pattern.
        """
        try:
            file_service = await make(FileService)

            matches = await file_service.find_project_files(text)
            return [f for f in matches if not await file_service.is_file_in_context(f)]
        except Exception:
            return []
