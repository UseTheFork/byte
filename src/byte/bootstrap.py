from rich.console import Console

from byte.container import app
from byte.core.config.config import ByteConfg
from byte.core.event_bus import EventBus
from byte.core.task_manager import TaskManager
from byte.domain.agent.service_provider import AgentServiceProvider
from byte.domain.analytics.service_provider import AnalyticsProvider
from byte.domain.cli_input.service.command_registry import CommandRegistry
from byte.domain.cli_input.service_provider import CliInputServiceProvider
from byte.domain.cli_output.service_provider import CliOutputServiceProvider
from byte.domain.edit_format.service_provider import EditFormatProvider
from byte.domain.files.service_provider import FileServiceProvider
from byte.domain.git.service_provider import GitServiceProvider
from byte.domain.lint.service_provider import LintServiceProvider
from byte.domain.llm.service_provider import LLMServiceProvider
from byte.domain.mcp.service_provider import MCPServiceProvider
from byte.domain.memory.service_provider import MemoryServiceProvider
from byte.domain.system.service_provider import SystemServiceProvider
from byte.domain.tools.service_provider import ToolsServiceProvider


async def bootstrap(config: ByteConfg):
    """Initialize and configure the application's dependency injection container.

    Follows a two-phase initialization pattern: register all services first,
    then boot them. This ensures all dependencies are available during the
    boot phase when services may need to reference each other.

    Returns the fully configured container ready for use.
    """

    app.singleton(EventBus)
    app.singleton(TaskManager)

    # Make the global command registry available through dependency injection
    app.singleton(CommandRegistry)

    app.singleton(ByteConfg, lambda: config)

    console = Console()
    app.singleton(Console, lambda: console)

    # Order matters: ConfigServiceProvider must be early since other services
    # may need configuration access during their boot phase

    service_providers = [
        CliInputServiceProvider(),  # Console and prompt services
        CliOutputServiceProvider(),  # Console and prompt services
        MemoryServiceProvider(),  # Short-term conversation memory
        # KnowledgeServiceProvider(),  # Long-term knowledge storage
        FileServiceProvider(),  # File context management
        ToolsServiceProvider(),  # File context management
        LLMServiceProvider(),  # Language model integration
        GitServiceProvider(),  # Git repository operations
        LintServiceProvider(),  # Code linting functionality
        AgentServiceProvider(),  # Agent routing and management
        MCPServiceProvider(),
        AnalyticsProvider(),
        EditFormatProvider(),
        SystemServiceProvider(),  # Core system commands
    ]

    # Phase 1: Register all service bindings in the container
    # This makes services available for dependency resolution
    for provider in service_providers:
        await provider.register_services(app)
        await provider.register_commands(app)
        await provider.register(app)

    # Phase 2: Boot services after all are registered
    # This allows services to safely reference dependencies during initialization
    for provider in service_providers:
        await provider.boot_commands(app)
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
