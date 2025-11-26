from argparse import Namespace

from byte.core.config.config import PROJECT_ROOT
from byte.core.utils import dump
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.lsp.service.lsp_service import LSPService


class TestCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "dev:test"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """ """
        console = await self.make(ConsoleService)
        lsp_service = await self.make(LSPService)

        path = PROJECT_ROOT / "src/byte/domain/web/service/chromium_service.py"

        if not path.exists():
            console.print(f"[red]File does not exist: {path}[/red]")
            return

        console.print(f"[green]Testing LSP on: {path}[/green]")
        console.print(f"[yellow]File URI: {path.as_uri()}[/yellow]")

        # result = await lsp_service.handle(operation="hover", file_path=path, line=0, character=10)
        # result = await lsp_service.goto_declaration(file_path=path, line=0, character=10)
        # result = await lsp_service.goto_declaration(file_path=path, line=13, character=6)
        # result = await lsp_service.goto_declaration(file_path=path, line=12, character=15)
        result = await lsp_service.get_diagnostics(file_path=path)
        dump(result)

        result = await lsp_service.goto_declaration(file_path=path, line=40, character=28)
        # result = await lsp_service.get_hover(file_path=path, line=12, character=15)
        dump(result)
