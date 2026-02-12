from argparse import Namespace
from urllib.parse import urlparse

from byte.cli import ByteArgumentParser, Command


class ContextAddCommand(Command):
    """Smart command that detects and adds either files or URLs to session context.

    Automatically detects whether the input is a file path or URL and proxies
    to the appropriate command (ContextAddFileCommand or WebCommand).
    Usage: `/ctx:add path/to/file.py` or `/ctx:add https://example.com`
    """

    @property
    def name(self) -> str:
        return "context"

    @property
    def category(self) -> str:
        return "Session Context"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Add a file or URL to session context. Automatically detects the type and handles appropriately.",
        )
        parser.add_argument("target", help="Path to file or URL to add")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Detect input type and proxy to appropriate command.

        Usage: `await command.execute("config.py")` or `await command.execute("https://example.com")`
        """
        from byte.knowledge.command.context_add_file_command import ContextAddFileCommand
        from byte.knowledge.command.web_command import WebCommand

        target = args.target

        # Detect if target is a URL
        parsed = urlparse(target)
        is_url = parsed.scheme in ("http", "https")

        if is_url:
            # Proxy to WebCommand
            web_command = self.app.make(WebCommand)
            web_args = Namespace(url=target)
            await web_command.execute(web_args, raw_args)
        else:
            # Proxy to ContextAddFileCommand
            file_command = self.app.make(ContextAddFileCommand)
            file_args = Namespace(file_path=target)
            await file_command.execute(file_args, raw_args)
