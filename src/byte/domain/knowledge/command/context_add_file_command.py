from argparse import Namespace
from pathlib import Path

from byte.core.config.config import ByteConfg
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.knowledge.models import SessionContextModel
from byte.domain.knowledge.service.session_context_service import SessionContextService


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
        console = await self.make(ConsoleService)

        args_file_path = args.file_path

        config = await self.make(ByteConfg)
        session_context_service = await self.make(SessionContextService)

        # Convert to Path object, resolve relative paths from project root
        file_path = Path(args_file_path)
        if not file_path.is_absolute():
            file_path = config.project_root / file_path

        # Check if file exists
        if not file_path.exists():
            console.print(f"[error]File not found: {args_file_path}[/error]")
            return

        if not file_path.is_file():
            console.print(f"[error]Path is not a file: {args_file_path}[/error]")
            return

        # Read file contents
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[error]Error reading file: {e!s}[/error]")
            return

        context_key = str(file_path.relative_to(config.project_root))

        # Add YAML header with file path
        yaml_header = f"---\nfile_path: {context_key}\n---\n\n"
        content = yaml_header + content
        model = await self.make(SessionContextModel, type="file", key=context_key, content=content)
        session_context_service.add_context(model)
        console.print(f"[success]Added {context_key} to session context[/success]")
