from typing import TYPE_CHECKING, List

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

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

    async def pre_prompt(self) -> None:
        """Display current editable files before each prompt.

        Provides visual feedback about which files the AI can modify,
        helping users understand the current context state.
        """
        if not self.container:
            return
        file_service = await make(FileService)
        editable_files = file_service.list_files(FileMode.EDITABLE)
        if not editable_files:
            return

        console = await make(Console)

        file_names = [f"[info]{f.relative_path}[/info]" for f in editable_files]
        console.print(
            Panel(
                Columns(file_names, equal=True, expand=True),
                title="[bold success]Editable Files[/bold success]",
                border_style="success",
            )
        )


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

    async def pre_prompt(self) -> None:
        """Display current read-only files before each prompt.

        Shows which files are available for AI reference, using different
        styling to distinguish from editable files in the UI.
        """
        if not self.container:
            return
        file_service: FileService = await make(FileService)
        readonly_files = file_service.list_files(FileMode.READ_ONLY)
        if not readonly_files:
            return

        console: Console = await make(Console)

        file_names = [f"[warning]{f.relative_path}[/warning]" for f in readonly_files]
        console.print(
            Panel(
                Columns(file_names, equal=True, expand=True),
                title="[bold info]Read-only Files[/bold info]",
                border_style="info",
            )
        )


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
        """Complete with files currently in context for accurate removal.

        Only suggests files that are actually in context, preventing
        errors and providing immediate feedback about available files.
        """
        try:
            return []

            import asyncio

            from byte.context import get_container

            container = get_container()
            file_service = asyncio.run(container.make(FileService))

            files = file_service.list_files()
            return [f.relative_path for f in files if f.relative_path.startswith(text)]
        except Exception:
            return []
