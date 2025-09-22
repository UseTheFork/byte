from typing import List, Type

from byte.container import Container
from byte.core.actors.base import Actor
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.agent.actor.agent_actor import AgentActor
from byte.domain.agent.base import Agent
from byte.domain.agent.coder.agent import CoderAgent
from byte.domain.agent.service.agent_service import AgentService


class AgentServiceProvider(ServiceProvider):
    """Main service provider for all agent types and routing.

    Manages registration and initialization of specialized AI agents (coder, docs, ask)
    and provides the central agent switching functionality. Coordinates between
    different agent implementations while maintaining a unified interface.
    Usage: Automatically registered during bootstrap to enable agent routing
    """

    def services(self) -> List[Type[Service]]:
        return [AgentService]

    def actors(self) -> List[Type[Actor]]:
        return [AgentActor]

    def agents(self) -> List[Type[Agent]]:
        return [CoderAgent]

    async def register(self, container: "Container") -> None:
        # Create all agents
        for agent_class in self.agents():
            container.singleton(agent_class)

    async def boot(self, container: "Container") -> None:
        """Boot all sub-agents and register agent switching commands.

        Initializes all registered agents and registers the /agent command for
        switching between different AI agents during runtime.
        """
        pass
