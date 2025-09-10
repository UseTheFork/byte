import os
from typing import List

from rich.columns import Columns
from rich.console import Console

from byte.core.command.registry import Command

from .context_manager import FileMode


class AddFileCommand(Command):
    @property
    def name(self) -> str:
        return "add"

    @property
    def description(self) -> str:
        return "Add file to context as editable"

    async def execute(self, args: str) -> str:
        if not args:
            return "Usage: /add <file_path>"

        file_service = self.container.make("file_service")
        if await file_service.add_file(args, FileMode.EDITABLE):
            return f"Added {args} to context as editable"
        else:
            return f"Failed to add {args} (file not found or not readable)"

    def get_completions(self, text: str) -> List[str]:
        """File path completions."""
        try:
            if "/" in text:
                directory = os.path.dirname(text)
                prefix = os.path.basename(text)
            else:
                directory = "."
                prefix = text

            if os.path.exists(directory):
                items = []
                for item in os.listdir(directory):
                    if item.startswith(prefix):
                        full_path = (
                            os.path.join(directory, item) if directory != "." else item
                        )
                        if os.path.isfile(full_path):
                            items.append(full_path)
                return items
        except (OSError, PermissionError):
            pass
        return []

    def pre_prompt(self, console: Console) -> None:
        """Display editable files."""
        if not self.container:
            return
        file_service = self.container.make("file_service")
        editable_files = file_service.list_files(FileMode.EDITABLE)
        if not editable_files:
            return

        file_names = [f"[cyan]{f.relative_path}[/cyan]" for f in editable_files]
        console.print("[bold green]Editable Files:[/bold green]")
        console.print(Columns(file_names, equal=True, expand=True))
        console.print()


class ReadOnlyCommand(Command):
    @property
    def name(self) -> str:
        return "read-only"

    @property
    def description(self) -> str:
        return "Add file to context as read-only"

    async def execute(self, args: str) -> str:
        if not args:
            return "Usage: /read-only <file_path>"

        file_service = self.container.make("file_service")
        if await file_service.add_file(args, FileMode.READ_ONLY):
            return f"Added {args} to context as read-only"
        else:
            return f"Failed to add {args} (file not found or not readable)"

    def get_completions(self, text: str) -> List[str]:
        """File path completions."""
        try:
            if "/" in text:
                directory = os.path.dirname(text)
                prefix = os.path.basename(text)
            else:
                directory = "."
                prefix = text

            if os.path.exists(directory):
                items = []
                for item in os.listdir(directory):
                    if item.startswith(prefix):
                        full_path = (
                            os.path.join(directory, item) if directory != "." else item
                        )
                        if os.path.isfile(full_path):
                            items.append(full_path)
                return items
        except (OSError, PermissionError):
            pass
        return []

    def pre_prompt(self, console: Console) -> None:
        """Display read-only files."""
        if not self.container:
            return
        file_service = self.container.make("file_service")
        readonly_files = file_service.list_files(FileMode.READ_ONLY)
        if not readonly_files:
            return

        file_names = [f"[yellow]{f.relative_path}[/yellow]" for f in readonly_files]
        console.print("[bold blue]Read-only Files:[/bold blue]")
        console.print(Columns(file_names, equal=True, expand=True))
        console.print()


class DropFileCommand(Command):
    def __init__(self, container=None):
        self.container = container

    @property
    def name(self) -> str:
        return "drop"

    @property
    def description(self) -> str:
        return "Remove file from context"

    async def execute(self, args: str) -> str:
        if not args:
            return "Usage: /drop <file_path>"

        file_service = self.container.make("file_service")
        if await file_service.remove_file(args):
            return f"Removed {args} from context"
        else:
            return f"File {args} not found in context"

    def get_completions(self, text: str) -> List[str]:
        """Complete with files currently in context."""
        if not self.container:
            return []
        file_service = self.container.make("file_service")
        files = file_service.list_files()
        return [f.relative_path for f in files if f.relative_path.startswith(text)]
