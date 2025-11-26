from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.knowledge.command.context_add_file_command import ContextAddFileCommand
from byte.domain.knowledge.command.context_drop_command import ContextDropCommand
from byte.domain.knowledge.command.context_list_command import ContextListCommand
from byte.domain.knowledge.command.web_command import WebCommand
from byte.domain.knowledge.models import SessionContextModel
from byte.domain.knowledge.service.cli_context_display_service import (
    CLIContextDisplayService,
)
from byte.domain.knowledge.service.convention_context_service import (
    ConventionContextService,
)
from byte.domain.knowledge.service.session_context_service import SessionContextService


class KnowledgeServiceProvider(ServiceProvider):
    """Service provider for long-term knowledge management.

    Registers knowledge services for persistent storage of user preferences,
    project patterns, and learned behaviors. Enables cross-session memory
    and intelligent context building for the AI agent system.
    Usage: Register with container to enable long-term knowledge storage
    """

    def services(self) -> List[Type[Service]]:
        return [
            ConventionContextService,
            SessionContextService,
            CLIContextDisplayService,
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            WebCommand,
            ContextListCommand,
            ContextDropCommand,
            ContextAddFileCommand,
        ]

    async def register(self, container: Container):
        container.bind(SessionContextModel)

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""

        # Set up event listener for PRE_PROMPT_TOOLKIT
        event_bus = await container.make(EventBus)
        conventions_service = await container.make(ConventionContextService)
        session_context_service = await container.make(SessionContextService)

        cli_context_display_service = await container.make(CLIContextDisplayService)

        # Register listener that calls list_in_context_files before each prompt
        event_bus.on(
            EventType.GATHER_PROJECT_CONTEXT.value,
            conventions_service.add_project_context_hook,
        )

        # Register listener that calls list_in_context_files before each prompt
        event_bus.on(
            EventType.GATHER_PROJECT_CONTEXT.value,
            session_context_service.add_session_context_hook,
        )

        event_bus.on(
            EventType.PRE_PROMPT_TOOLKIT.value,
            cli_context_display_service.display_context_panel_hook,
        )
