from typing import Type

from byte.core.service.base_service import Service
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.coder.agent import CoderAgent


class AgentService(Service):
    """Main agent service that provides runnables for streaming."""

    _current_agent: Type[Agent] = CoderAgent

    async def boot(self):
        """Boot method to initialize the agent service."""
        self._current_agent = CoderAgent  # Set default agent
        self._agent_instances = {}

        # Available agent types
        self._available_agents = [
            CoderAgent,
            # Add more agents here as they're implemented
        ]

    async def execute_current_agent(self, messages: list) -> dict:
        """Execute the currently active agent with the provided messages.

        Usage: result = await agent_service.execute_current_agent([("user", "Hello")])
        """
        if self._current_agent not in self._agent_instances:
            # Lazy load current agent
            agent_instance = await self.make(self._current_agent)
            self._agent_instances[self._current_agent] = agent_instance

        agent = self._agent_instances[self._current_agent]
        return await agent.execute({"messages": messages})

    def set_active_agent(self, agent_type: Type[Agent]) -> bool:
        """Switch the active agent."""
        if self._is_valid_agent(agent_type):
            self._current_agent = agent_type
            return True
        return False

    def _is_valid_agent(self, agent_type: Type[Agent]) -> bool:
        """Check if the agent type is valid."""
        return agent_type in self._available_agents

    def get_active_agent_type(self) -> Type[Agent]:
        """Get the currently active agent type."""
        return self._current_agent

    def get_available_agents(self) -> list[Type[Agent]]:
        """Get list of available agent types."""
        return self._available_agents

    def get_active_agent_name(self) -> str:
        """Get the name of the currently active agent for display purposes."""
        return self._current_agent.__name__.replace("Agent", "").lower()
