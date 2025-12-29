from typing import List, Type

from byte import Container
from byte.core import EventBus, EventType, Payload, Service, ServiceProvider
from byte.domain.cli import Command, ConsoleService
from byte.domain.memory import UndoCommand
from byte.domain.system import ConfigWriterService, ExitCommand, SystemContextService


class SystemServiceProvider(ServiceProvider):
    """Service provider for system-level commands and functionality.

    Registers core system commands like exit and help, making them available
    through the command registry for user interaction via slash commands.
    Usage: Register with container to enable /exit and /help commands
    """

    def commands(self) -> List[Type[Command]]:
        return [
            ExitCommand,
            UndoCommand,
        ]

    def services(self) -> List[Type[Service]]:
        return [
            SystemContextService,
            ConfigWriterService,
        ]

    async def boot(self, container: Container) -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """

        event_bus = await container.make(EventBus)
        system_context_service = await container.make(SystemContextService)

        event_bus.on(
            EventType.GATHER_PROJECT_CONTEXT.value,
            system_context_service.add_system_context,
        )

        # Emit our post boot message to gather all needed info.
        payload = await event_bus.emit(
            payload=Payload(
                event_type=EventType.POST_BOOT,
                data={
                    "messages": [],
                    "container": container,
                },
            )
        )

        console = await container.make(ConsoleService)
        messages = payload.get("messages", [])

        # Join all message strings into a single string with newlines
        panel_content = "\n".join(messages)

        # Display the assembled messages inside a panel
        console.print_panel(panel_content, border_style="primary")
