from __future__ import annotations

from typing import TYPE_CHECKING, List, Type

from byte import Command, EventBus, Service, ServiceProvider, TaskManager
from byte.lsp import LSPService
from byte.system import SystemEvents

if TYPE_CHECKING:
    from byte.foundation import Application


class LSPServiceProvider(ServiceProvider):
    """Service provider for Language Server Protocol integration.

    Registers LSP services for multi-language code intelligence features
    like hover information, references, definitions, and completions.
    Usage: Register with container to enable LSP functionality
    """

    def services(self) -> List[Type[Service]]:
        """Return list of LSP services to register."""
        return [LSPService]

    def commands(self) -> List[Type[Command]]:
        """Return list of LSP commands to register."""
        return []

    async def boot(self):
        config = self.app["config"]
        if config.lsp.enable:
            # Boots the LSPs and starts them in the background.
            self.app.make(LSPService)
            event_bus = self.app.make(EventBus)

            event_bus.on(
                SystemEvents.PostBoot,
                self.boot_messages,
            )

    async def boot_messages(self, payload: SystemEvents.PostBoot) -> SystemEvents.PostBoot:
        task_manager = self.app.make(TaskManager)

        running_count = sum(1 for name in task_manager._tasks.keys() if name.startswith("lsp_server_"))

        payload.messages.append(f"[text-muted]LSP servers running:[/text-muted] [$primary]{running_count}[/$primary]")

        return payload

    async def shutdown(self, app: Application) -> None:
        """Shutdown all LSP servers gracefully."""
        config = self.app["config"]
        if config.lsp.enable:
            lsp_service = app.make(LSPService)
            await lsp_service.shutdown_all()
