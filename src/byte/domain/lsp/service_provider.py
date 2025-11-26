from typing import List, Type

from byte.container import Container
from byte.core.config.config import ByteConfg
from byte.core.event_bus import EventBus, EventType, Payload
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.core.task_manager import TaskManager
from byte.domain.cli.service.command_registry import Command
from byte.domain.lsp.service.lsp_service import LSPService


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

    async def boot(self, container: Container):
        config = await container.make(ByteConfg)
        if config.lsp.enable:
            # Boots the LSPs and starts them in the background.
            await container.make(LSPService)
            event_bus = await container.make(EventBus)

            event_bus.on(
                EventType.POST_BOOT.value,
                self.boot_messages,
            )

    async def boot_messages(self, payload: Payload) -> Payload:
        container: Container = payload.get("container", False)
        if container:
            task_manager = await container.make(TaskManager)

            running_count = sum(1 for name in task_manager._tasks.keys() if name.startswith("lsp_server_"))

            messages = payload.get("messages", [])
            messages.append(f"[muted]LSP servers running:[/muted] [primary]{running_count}[/primary]")

            payload.set("messages", messages)

        return payload

    async def shutdown(self, container: Container) -> None:
        """Shutdown all LSP servers gracefully."""
        config = await container.make(ByteConfg)
        if config.lsp.enable:
            lsp_service = await container.make(LSPService)
            await lsp_service.shutdown_all()
