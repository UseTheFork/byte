from typing import Type

from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable, Injectable
from byte.domain.agent.base import BaseAgent
from byte.domain.agent.coder.service import CoderAgent


class AgentService(Bootable, Configurable, Injectable):
    """Main agent service that routes requests to specialized agents."""

    _current_agent: Type[BaseAgent] = CoderAgent

    async def boot(self):
        """Boot method to initialize the agent service."""
        self._current_agent = CoderAgent  # Set default agent
        self._agents = {}

        # Available agent types
        self._available_agents = [
            CoderAgent,
            # Add more agents here as they're implemented
            # DocsService,
            # AskService,
        ]

    async def route_to_agent(self, agent_type: Type[BaseAgent], request: str):
        """Route request to the specified agent."""

        if agent_type not in self._agents:
            # Lazy load agent
            if not self._is_valid_agent(agent_type):
                raise ValueError(f"Unknown agent type: {agent_type}")

            agent_service = await self.make(agent_type)
            self._agents[agent_type] = agent_service

        agent = self._agents[agent_type]

        # Return the async generator directly, don't await it
        async for event in agent.stream(request):
            yield event

    def set_active_agent(self, agent_type: Type[BaseAgent]) -> bool:
        """Switch the active agent."""
        if self._is_valid_agent(agent_type):
            self._current_agent = agent_type
            return True
        return False

    def _is_valid_agent(self, agent_type: Type[BaseAgent]) -> bool:
        """Check if the agent type is valid."""
        return agent_type in self._available_agents

    def get_active_agent(self) -> Type[BaseAgent]:
        """Get the currently active agent type."""
        return self._current_agent

    def get_available_agents(self) -> list[Type[BaseAgent]]:
        """Get list of available agent types."""
        return self._available_agents

    def get_active_agent_name(self) -> str:
        """Get the name of the currently active agent for display purposes."""
        return self._current_agent.__name__.replace("Service", "").lower()
