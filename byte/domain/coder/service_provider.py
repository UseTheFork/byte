from typing import TYPE_CHECKING

from byte.core.service_provider import ServiceProvider
from byte.domain.coder.commands import CoderCommand
from byte.domain.coder.config import CoderConfig
from byte.domain.coder.service import CoderService

if TYPE_CHECKING:
    from byte.container import Container


class CoderServiceProvider(ServiceProvider):
    """Service provider for the coder agent domain.

    Registers the specialized coder agent for software development tasks
    including code generation, debugging, refactoring, and analysis.
    Integrates with file context, memory, and development tools.
    Usage: Register with container to enable coder agent functionality
    """

    async def register(self, container: "Container") -> None:
        """Register coder agent services in the container.

        Usage: `provider.register(container)` -> binds coder services
        """
        # Register coder config schema
        config_service = await container.make("config")
        config_service.register_schema("coder", CoderConfig)

        # Register coder service
        container.singleton("coder_service", lambda: CoderService(container))

        # Register coder command
        container.bind("coder_command", lambda: CoderCommand(container))

    async def boot(self, container: "Container") -> None:
        """Boot coder services after all providers are registered.

        Usage: `provider.boot(container)` -> coder agent ready for development tasks
        """
        command_registry = await container.make("command_registry")

        # Register coder command for user access
        await command_registry.register_slash_command(
            await container.make("coder_command")
        )

        # Coder service is lazy-loaded, no explicit boot needed
        # Tools will be registered by their respective domains

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["coder_service", "coder_command"]
