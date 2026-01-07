from __future__ import annotations

from typing import TYPE_CHECKING, List, Type

from byte import EventBus, EventType, Payload, Service, ServiceProvider, TaskManager
from byte.cli import Command
from byte.lsp import LSPService

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
                EventType.POST_BOOT.value,
                self.boot_messages,
            )

    async def boot_messages(self, payload: Payload) -> Payload:
        container: Application = payload.get("container", False)
        if container:
            task_manager = await container.make(TaskManager)

            running_count = sum(1 for name in task_manager._tasks.keys() if name.startswith("lsp_server_"))

            messages = payload.get("messages", [])
            messages.append(f"[muted]LSP servers running:[/muted] [primary]{running_count}[/primary]")

            payload.set("messages", messages)

        return payload

    async def shutdown(self, container: Application) -> None:
        """Shutdown all LSP servers gracefully."""
        config = self.app["config"]
        if config.lsp.enable:
            lsp_service = await container.make(LSPService)
            await lsp_service.shutdown_all()
