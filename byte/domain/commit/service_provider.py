from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.commit.commands import CommitCommand


class CommitServiceProvider(ServiceProvider):
    """Service provider for commit functionality."""

    def register(self, container: Container):
        """Register commit commands in the container."""
        container.bind("commit_command", lambda: CommitCommand(container))

    def boot(self, container: Container):
        """Boot commit services and register commands with registry."""
        # Get the command registry
        command_registry = container.make("command_registry")

        # Register commit command
        command_registry.register_slash_command(container.make("commit_command"))

    def provides(self) -> list:
        return ["commit_command"]
