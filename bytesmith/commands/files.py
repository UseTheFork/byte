import os
from typing import List

from bytesmith.commands.registry import Command, command_registry
from bytesmith.context.file_manager import FileMode, file_context_manager


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


class SetModeCommand(Command):
    @property
    def name(self) -> str:
        return "mode"

    @property
    def description(self) -> str:
        return "Set file mode (readonly/editable)"

    async def execute(self, args: str) -> str:
        parts = args.split()
        if len(parts) != 2:
            return "Usage: /mode <file_path> <readonly|editable>"

        file_path, mode_str = parts

        if mode_str.lower() in ["readonly", "read-only"]:
            mode = FileMode.READ_ONLY
        elif mode_str.lower() == "editable":
            mode = FileMode.EDITABLE
        else:
            return "Mode must be 'readonly' or 'editable'"

        if file_context_manager.set_file_mode(file_path, mode):
            return f"Set {file_path} to {mode_str}"
        else:
            return f"File {file_path} not found in context"


# Auto-register commands
command_registry.register_slash_command(AddFileCommand())
command_registry.register_slash_command(ReadOnlyCommand())
command_registry.register_slash_command(DropFileCommand())
command_registry.register_slash_command(SetModeCommand())
