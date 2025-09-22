from typing import List, Type

from byte.container import Container
from byte.core.actors.base import Actor
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli_input.actor.input_actor import InputActor
from byte.domain.lint.actor.lint_actor import LintActor
from byte.domain.lint.service.lint_service import LintService


class LintServiceProvider(ServiceProvider):
    """Service provider for code linting functionality.

    Registers AI-integrated linting service that can analyze code quality
    and formatting issues. Integrates with the command registry and provides
    programmatic access for agent workflows.
    Usage: Register with container to enable `/lint` command and lint service
    """

    def services(self) -> List[Type[Service]]:
        return [LintService]

    def actors(self) -> List[Type[Actor]]:
        return [LintActor]

    async def register(self, container: "Container") -> None:
        """Register lint services in the container.

        Usage: `provider.register(container)` -> binds lint service and command
        """
        # Register lint service and command
        container.singleton(LintService)

    async def boot(self, container: "Container") -> None:
        """Boot lint services and register commands with registry.

        Usage: `provider.boot(container)` -> `/lint` becomes available to users
        """

        input_actor = await container.make(InputActor)
        await input_actor.register_command_handler("lint", LintActor)
