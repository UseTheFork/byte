from byte import EventBus, ServiceProvider
from byte.memory import UndoCommand
from byte.orchestration import OrchestrationEvents
from byte.system import (
    ExitCommand,
    SystemContextService,
    UserConfirmOrInputTool,
    UserConfirmTool,
    UserInputTextTool,
    UserSelectTool,
)


class SystemServiceProvider(ServiceProvider):
    """Service provider for system-level commands and functionality.

    Registers core system commands like exit and help, making them available
    through the command registry for user interaction via slash commands.
    Usage: Register with container to enable /exit and /help commands
    """

    def tools(self):
        """"""
        return [
            # keep-sorted start
            UserConfirmOrInputTool,
            UserConfirmTool,
            UserInputTextTool,
            UserSelectTool,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            ExitCommand,
            UndoCommand,
            # keep-sorted end
        ]

    def services(self):
        return [
            # keep-sorted start
            SystemContextService,
            # ConfigWriterService,
            # keep-sorted end
        ]

    async def boot(self) -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """

        event_bus = self.app.make(EventBus)
        system_context_service = self.app.make(SystemContextService)

        event_bus.on(
            OrchestrationEvents.GatherReinforcement,
            system_context_service.add_system_context,
        )

        # # Emit our post boot message to gather all needed info.
        # payload = await event_bus.emit(
        #     payload=Payload(
        #         event_type=EventType.POST_BOOT,
        #         data={
        #             "messages": [],
        #         },
        #     )
        # )

        # console = self.app["console"]
        # messages = payload.get("messages", [])

        # # Join all message strings into a single string with newlines
        # panel_content = "\n".join(messages)

        # # Display the assembled messages inside a panel
        # console.print_panel(panel_content, border_style="primary")
