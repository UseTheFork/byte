from byte.application import app
from byte.core import ByteConfig
from byte.core.event_bus import EventBus
from byte.core.task_manager import TaskManager
from byte.domain.agent import AgentServiceProvider
from byte.domain.analytics import AnalyticsProvider
from byte.domain.cli import CLIServiceProvider, CommandRegistry, ConsoleService
from byte.domain.development.service_provider import DevelopmentProvider
from byte.domain.files import FileServiceProvider
from byte.domain.git import GitServiceProvider
from byte.domain.knowledge import KnowledgeServiceProvider
from byte.domain.lint import LintServiceProvider
from byte.domain.llm import LLMServiceProvider
from byte.domain.lsp import LSPServiceProvider
from byte.domain.memory import MemoryServiceProvider
from byte.domain.presets import PresetsProvider
from byte.domain.prompt_format import PromptFormatProvider
from byte.domain.system import SystemServiceProvider
from byte.domain.tools import ToolsServiceProvider
from byte.domain.web import WebServiceProvider


async def bootstrap(config: ByteConfig):
    """Initialize and configure the application's dependency injection container.

    Follows a two-phase initialization pattern: register all services first,
    then boot them. This ensures all dependencies are available during the
    boot phase when services may need to reference each other.

    Returns the fully configured container ready for use.
    """

    app.boot(config.project_root)

    app.singleton(EventBus)
    app.singleton(TaskManager)

    # Make the global command registry available through dependency injection
    app.singleton(CommandRegistry)

    # Boot config as early as possible
    app.singleton(ByteConfig, lambda: config)

    # Setup console early
    app.singleton(ConsoleService)

    # Order matters: ConfigServiceProvider must be early since other services
    # may need configuration access during their boot phase

    service_providers = [
        CLIServiceProvider(),  # Console and prompt services
        MemoryServiceProvider(),  # Short-term conversation memory
        KnowledgeServiceProvider(),
        FileServiceProvider(),  # File context management
        ToolsServiceProvider(),  # File context management
        LLMServiceProvider(),  # Language model integration
        GitServiceProvider(),  # Git repository operations
        LintServiceProvider(),  # Code linting functionality
        AgentServiceProvider(),  # Agent routing and management
        LSPServiceProvider(),
        AnalyticsProvider(),
        PromptFormatProvider(),
        WebServiceProvider(),
        PresetsProvider(),
        SystemServiceProvider(),  # Core system commands
        DevelopmentProvider(),  # Core system commands
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

    # Reset the global app container to ensure clean state
    app.reset()
