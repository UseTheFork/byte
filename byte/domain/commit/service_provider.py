from typing import TYPE_CHECKING

from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.commit.commands import CommitCommand

if TYPE_CHECKING:
    from byte.container import Container


class CommitServiceProvider(ServiceProvider):
    """Service provider for git commit functionality.

    Registers AI-powered commit command that generates conventional commit
    messages from staged changes. Integrates with the command registry to
    make commit functionality available via slash commands.
    Usage: Register with container to enable `/commit` command
    """

    async def register(self, container: "Container") -> None:
        """Register commit commands in the container.

        Usage: `provider.register(container)` -> binds commit command
        """
        # Register commit command
        container.bind("commit_command", lambda: CommitCommand(container))

    async def boot(self, container: "Container") -> None:
        """Boot commit services and register commands with registry.

        Usage: `provider.boot(container)` -> `/commit` becomes available to users
        """
        command_registry = await container.make("command_registry")

        # Register commit command for user access
        await command_registry.register_slash_command(
            await container.make("commit_command")
        )

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["commit_command"]
