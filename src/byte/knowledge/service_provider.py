from byte import EventBus, ServiceProvider
from byte.knowledge import (
    AddFilesToContextTool,
    ContextAddFileCommand,
    ContextDropCommand,
    ContextListCommand,
    SessionContextModel,
    SessionContextService,
    WebCommand,
)
from byte.knowledge.command.context_add_command import ContextAddCommand
from byte.orchestration import OrchestrationEvents


class KnowledgeServiceProvider(ServiceProvider):
    """Service provider for long-term knowledge management.

    Registers knowledge services for persistent storage of user preferences,
    project patterns, and learned behaviors. Enables cross-session memory
    and intelligent context building for the AI agent system.
    Usage: Register with container to enable long-term knowledge storage
    """

    def services(self):
        return [
            # keep-sorted start
            SessionContextService,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            ContextAddCommand,
            ContextAddFileCommand,
            ContextDropCommand,
            ContextListCommand,
            WebCommand,
            # keep-sorted end
        ]

    def tools(self):
        """"""
        return [
            # keep-sorted start
            AddFilesToContextTool,
            # keep-sorted end
        ]

    def register(self):
        self.app.bind(SessionContextModel)

    async def boot(self):
        """Boot file services and register commands with registry."""

        # Set up event listener for PRE_PROMPT_TOOLKIT
        event_bus = self.app.make(EventBus)
        session_context_service = self.app.make(SessionContextService)

        # Register listener that calls list_in_context_files before each prompt
        event_bus.on(
            OrchestrationEvents.GatherProjectContext,
            session_context_service.add_session_context_hook,
        )
