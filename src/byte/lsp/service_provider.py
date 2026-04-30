from __future__ import annotations

from typing import TYPE_CHECKING, List, Type

from byte import Command, Service, ServiceProvider
from byte.lsp import FindReferencesTool, GetDefinitionTool, GetHoverInfoTool, LSPService
from byte.tools import BaseTool

if TYPE_CHECKING:
    from byte.foundation import Application


class LSPServiceProvider(ServiceProvider):
    """Service provider for Language Server Protocol integration.

    Registers LSP services for multi-language code intelligence features
    like hover information, references, definitions, and completions.
    Usage: Register with container to enable LSP functionality
    """

    def tools(self) -> List[Type[BaseTool]]:
        return [
            GetHoverInfoTool,
            GetDefinitionTool,
            FindReferencesTool,
        ]

    def services(self) -> List[Type[Service]]:
        """Return list of LSP services to register."""
        return [LSPService]

    def commands(self) -> List[Type[Command]]:
        """Return list of LSP commands to register."""
        return []

    async def shutdown(self, app: Application) -> None:
        """Shutdown all LSP servers gracefully."""
        config = self.app["config"]
        if config.lsp.enable:
            lsp_service = app.make(LSPService)
            await lsp_service.shutdown_all()
