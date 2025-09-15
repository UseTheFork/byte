from byte.container import app
from byte.core.command.registry import command_registry
from byte.core.config.service_provider import ConfigServiceProvider
from byte.core.events.service_provider import EventServiceProvider
from byte.core.response.service_provider import ResponseServiceProvider
from byte.domain.agent.service_provider import AgentServiceProvider
from byte.domain.commit.service_provider import CommitServiceProvider
from byte.domain.files.file_service_provider import FileServiceProvider
from byte.domain.knowledge.service_provider import KnowledgeServiceProvider
from byte.domain.llm.service_provider import LLMServiceProvider
from byte.domain.memory.service_provider import MemoryServiceProvider
from byte.domain.system.service_provider import SystemServiceProvider
from byte.domain.ui.service_provider import UIServiceProvider


async def bootstrap():
    """Initialize and configure the application's dependency injection container.

    Follows a two-phase initialization pattern: register all services first,
    then boot them. This ensures all dependencies are available during the
    boot phase when services may need to reference each other.

    Returns the fully configured container ready for use.
    """
    # Make the global command registry available through dependency injection
    app.singleton("command_registry", lambda: command_registry)

    # Order matters: ConfigServiceProvider must be early since other services
    # may need configuration access during their boot phase
    service_providers = [
        ConfigServiceProvider(),  # Configuration management
        EventServiceProvider(),  # Foundation for domain events
        ResponseServiceProvider(),  # Agent response handling
        UIServiceProvider(),  # Console and prompt services
        MemoryServiceProvider(),  # Short-term conversation memory
        KnowledgeServiceProvider(),  # Long-term knowledge storage
        FileServiceProvider(),  # File context management
        LLMServiceProvider(),  # Language model integration
        CommitServiceProvider(),  # Git commit functionality
        AgentServiceProvider(),  # AI agent routing and management
        SystemServiceProvider(),  # Core system commands
    ]

    # Phase 1: Register all service bindings in the container
    # This makes services available for dependency resolution
    for provider in service_providers:
        await provider.register(app)

    # Phase 2: Boot services after all are registered
    # This allows services to safely reference dependencies during initialization
    for provider in service_providers:
        await provider.boot(app)

    # Store service providers for shutdown
    app._service_providers = service_providers

    return app


async def shutdown(container):
    """Shutdown all service providers in reverse order."""
    if hasattr(container, "_service_providers"):
        # Shutdown in reverse order (opposite of boot)
        for provider in reversed(container._service_providers):
            await provider.shutdown(container)
