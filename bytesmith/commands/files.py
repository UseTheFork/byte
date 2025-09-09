import os
from typing import List

from rich.columns import Columns
from rich.console import Console

from bytesmith.commands.registry import Command, command_registry
from bytesmith.context.file_manager import FileMode, file_context_manager


class ExitCommand(Command):
    @property
    def name(self) -> str:
        return "exit"

    @property
    def description(self) -> str:
        return "Exit ByteSmith"

    async def execute(self, args: str) -> str:
        # This will be handled specially in the main loop
        return "EXIT_REQUESTED"


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

        if file_context_manager.add_file(args, FileMode.EDITABLE):
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

    def display_pre_prompt_info(self, console: Console) -> None:
        """Display editable files."""
        editable_files = file_context_manager.list_files(FileMode.EDITABLE)
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

        if file_context_manager.add_file(args, FileMode.READ_ONLY):
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

    def display_pre_prompt_info(self, console: Console) -> None:
        """Display read-only files."""
        readonly_files = file_context_manager.list_files(FileMode.READ_ONLY)
        if not readonly_files:
            return

        file_names = [f"[yellow]{f.relative_path}[/yellow]" for f in readonly_files]
        console.print("[bold blue]Read-only Files:[/bold blue]")
        console.print(Columns(file_names, equal=True, expand=True))
        console.print()


class DropFileCommand(Command):
    @property
    def name(self) -> str:
        return "drop"

    @property
    def description(self) -> str:
        return "Remove file from context"

    async def execute(self, args: str) -> str:
        if not args:
            return "Usage: /drop <file_path>"

        if file_context_manager.remove_file(args):
            return f"Removed {args} from context"
        else:
            return f"File {args} not found in context"

    def get_completions(self, text: str) -> List[str]:
        """Complete with files currently in context."""
        files = file_context_manager.list_files()
        return [f.relative_path for f in files if f.relative_path.startswith(text)]


# Auto-register commands
command_registry.register_slash_command(AddFileCommand())
command_registry.register_slash_command(ReadOnlyCommand())
command_registry.register_slash_command(DropFileCommand())
command_registry.register_slash_command(ExitCommand())
