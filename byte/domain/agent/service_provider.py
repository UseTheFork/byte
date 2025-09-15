from typing import TYPE_CHECKING

from byte.core.service_provider import ServiceProvider
from byte.domain.agent.coder.service_provider import CoderServiceProvider
from byte.domain.agent.commands import SwitchAgentCommand
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

    async def register(self, container: "Container") -> None:
        container.singleton("agent_service", lambda: AgentService(container))

        # Register sub-agents
        coder_provider = CoderServiceProvider()
        await coder_provider.register(container)

    async def boot(self, container: "Container") -> None:
        """Boot all sub-agents and register agent switching commands.

        Initializes the coder agent and registers the /agent command for
        switching between different AI agents during runtime.
        """

        coder_provider = CoderServiceProvider()
        await coder_provider.boot(container)

        # Register agent switching commands
        command_registry = await container.make("command_registry")
        await command_registry.register_slash_command(SwitchAgentCommand(container))

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["coder_service", "coder_command"]
