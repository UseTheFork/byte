from typing import TYPE_CHECKING

from byte.core.events.dispatcher import EventDispatcher
from byte.core.service_provider import ServiceProvider
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
        container.bind("lint_service", lambda: LintService(container))
        container.bind("lint_command", lambda: LintCommand(container))

    async def boot(self, container: "Container") -> None:
        """Boot lint services and register commands with registry.

        Usage: `provider.boot(container)` -> `/lint` becomes available to users
        """
        command_registry = await container.make("command_registry")
        event_dispatcher: EventDispatcher = await container.make("event_dispatcher")
        lint_service: LintService = await container.make("lint_service")

        # Register lint command for user access
        await command_registry.register_slash_command(
            await container.make("lint_command")
        )

        # Register event listener for pre-commit linting
        event_dispatcher.listen("PreCommitStarted", lint_service.lint_changed_files)

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["lint_service", "lint_command"]
