from typing import TYPE_CHECKING

from byte.core.command.registry import CommandRegistry
from byte.core.service_provider import ServiceProvider
from byte.domain.events.dispatcher import EventDispatcher
from byte.domain.lint.commands import LintCommand
from byte.domain.lint.service import LintService

if TYPE_CHECKING:
    from byte.container import Container


class LintServiceProvider(ServiceProvider):
    """Service provider for code linting functionality.

    Registers AI-integrated linting service that can analyze code quality
    and formatting issues. Integrates with the command registry and provides
    programmatic access for agent workflows.
    Usage: Register with container to enable `/lint` command and lint service
    """

    async def register(self, container: "Container") -> None:
        """Register lint services in the container.

        Usage: `provider.register(container)` -> binds lint service and command
        """
        # Register lint service and command
        container.singleton(LintService)
        container.singleton(LintCommand)

    async def boot(self, container: "Container") -> None:
        """Boot lint services and register commands with registry.

        Usage: `provider.boot(container)` -> `/lint` becomes available to users
        """
        command_registry = await container.make(CommandRegistry)
        event_dispatcher = await container.make(EventDispatcher)
        lint_service = await container.make(LintService)

        # Register lint command for user access
        await command_registry.register_slash_command(await container.make(LintCommand))

        # Register event listener for pre-commit linting
        event_dispatcher.listen("PreCommitStarted", lint_service._handle_pre_commit)

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["lint_service", "lint_command"]
