from typing import List, Type

from byte.container import Container
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.agent.implementations.commit.agent import CommitAgent
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

    def agents(self) -> List[Type[Agent]]:
        return [CoderAgent, CommitAgent]

    async def register(self, container: "Container") -> None:
        # Create all agents
        for agent_class in self.agents():
            container.singleton(agent_class)
