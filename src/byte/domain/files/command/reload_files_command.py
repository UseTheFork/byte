from argparse import Namespace

from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.service.discovery_service import FileDiscoveryService


class ReloadFilesCommand(Command):
    """Command to reload the project file discovery cache.

    Rescans the project directory to update the cached file list,
    useful when files are added/removed outside of the application
    or when gitignore patterns change during development.
    Usage: `/reload` -> refreshes the file discovery cache
    """

    @property
    def name(self) -> str:
        return "reload"

    @property
    def category(self) -> str:
        return "Files"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Reload project file discovery cache",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Refresh the file discovery cache by rescanning the project."""
        console = await self.make(ConsoleService)

        file_discovery = await self.make(FileDiscoveryService)
        await file_discovery.refresh()

        console.print("[success]File discovery cache reloaded successfully[/success]")
