from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.agent.coder.service import CoderAgent


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

        # Register coder service
        container.singleton(CoderAgent)

        # Register coder command
        # container.bind(CoderCommand)

    async def boot(self, container: "Container") -> None:
        """Boot coder services after all providers are registered.

        Usage: `provider.boot(container)` -> coder agent ready for development tasks
        """
        # command_registry = await container.make(CommandRegistry)

        # # Register coder command for user access
        # await command_registry.register_slash_command(
        #     await container.make(CoderCommand)
        # )
