from typing import TYPE_CHECKING

from byte.core.command.registry import CommandRegistry
from byte.core.service_provider import ServiceProvider
from byte.domain.agent.coder.service_provider import CoderServiceProvider
from byte.domain.agent.commands import SwitchAgentCommand
from byte.domain.agent.commit.service_provider import CommitServiceProvider
from byte.domain.agent.service import AgentService

if TYPE_CHECKING:
    from byte.container import Container


class AgentServiceProvider(ServiceProvider):
    """Main service provider for all agent types and routing.

    Manages registration and initialization of specialized AI agents (coder, docs, ask)
    and provides the central agent switching functionality. Coordinates between
    different agent implementations while maintaining a unified interface.
    Usage: Automatically registered during bootstrap to enable agent routing
    """

    def __init__(self):
        super().__init__()
        self.agent_providers = [
            CoderServiceProvider(),
            CommitServiceProvider(),
        ]

    async def register(self, container: "Container") -> None:
        container.singleton(AgentService)

        # Register all sub-agents
        for provider in self.agent_providers:
            await provider.register(container)

    async def boot(self, container: "Container") -> None:
        """Boot all sub-agents and register agent switching commands.

        Initializes all registered agents and registers the /agent command for
        switching between different AI agents during runtime.
        """

        # Boot all sub-agents
        for provider in self.agent_providers:
            await provider.boot(container)

        # Register agent switching commands
        command_registry = await container.make(CommandRegistry)
        await command_registry.register_slash_command(SwitchAgentCommand(container))

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        services = ["agent_service"]
        # Collect services from all agent providers
        for provider in self.agent_providers:
            services.extend(provider.provides())
        return services
