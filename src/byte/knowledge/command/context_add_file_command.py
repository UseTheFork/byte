from argparse import Namespace
from pathlib import Path

from byte import ByteArgumentParser, Command
from byte.knowledge import SessionContextModel, SessionContextService
from byte.tui import Messages


class ContextAddFileCommand(Command):
    """Command to add file contents to session context.

    Reads a file from disk and adds its contents to the session context,
    making it available to the AI for reference during the conversation.
    Usage: `/ctx:file path/to/file.py` -> adds file contents to context
    """

    @property
    def name(self) -> str:
        return "ctx:file"

    @property
    def category(self) -> str:
        return "Session Context"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Read a file from disk and add its contents to the session context, making it available to the AI for reference during the conversation",
        )
        parser.add_argument("file_path", help="Path to file")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Read a file and add its contents to session context.

        Usage: `await command.execute("config.py")`
        """
        await self.emit_tui(Messages.CommandExecutionStarted())

        args_file_path = args.file_path

        session_context_service = self.app.make(SessionContextService)

        # Convert to Path object, resolve relative paths from project root
        file_path = Path(args_file_path)
        if not file_path.is_absolute():
            # self.app["path"]
            file_path = self.app.root_path(str(file_path))

        # Check if file exists
        if not file_path.exists():
            await self.notify_error(f"File not found: {args_file_path}")
            return

        if not file_path.is_file():
            await self.notify_error(f"Path is not a file: {args_file_path}")
            return

        # Read file contents
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            await self.notify_error(f"Error reading file: {e!s}")
            return

        context_key = str(file_path.relative_to(self.app["path"]))

        # Add YAML header with file path
        yaml_header = f"---\nfile_path: {context_key}\n---\n\n"
        content = yaml_header + content
        model = self.app.make(SessionContextModel, type="file", key=context_key, content=content)
        session_context_service.add_context(model)
        await self.notify_success(f"Added {context_key} to session context")

        await self.emit_tui(Messages.CommandExecutionCompleted())
