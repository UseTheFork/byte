from typing import Optional, Type

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

    async def execute_agent(self, input: str, agent: Optional[Type[Agent]] = None) -> dict:
        """Execute the currently active agent with the provided inputs.

        Args:
                input: String containing the user request
                agent: Optional specific agent type to execute. If None, uses current agent.

        Usage: result = await agent_service.execute_current_agent({"messages": [("user", "Hello")]})
        Usage: result = await agent_service.execute_current_agent({"messages": [("user", "Hello")]}, CoderAgent)
        """
        target_agent = agent if agent is not None else self._current_agent

        if target_agent not in self._agent_instances:
            # Lazy load target agent
            agent_instance = await self.make(target_agent)
            self._agent_instances[target_agent] = agent_instance

        agent_instance = self._agent_instances[target_agent]
        return await agent_instance.execute(input)

    def set_active_agent(self, agent_type: Type[Agent]) -> bool:
        """Switch the active agent."""
        if self._is_valid_agent(agent_type):
            self._current_agent = agent_type
            return True
        return False

    def get_active_agent(self) -> Type[Agent]:
        """Get the currently active agent type.

        Usage: current_agent = agent_service.get_active_agent()
        """
        return self._current_agent

    def _is_valid_agent(self, agent_type: Type[Agent]) -> bool:
        """Check if the agent type is valid."""
        return agent_type in self._available_agents

    def get_active_agent_type(self) -> Type[Agent]:
        """Get the currently active agent type."""
        return self._current_agent

    def get_available_agents(self) -> list[Type[Agent]]:
        """Get list of available agent types."""
        return self._available_agents  # pyright: ignore[reportReturnType]

    def get_active_agent_name(self) -> str:
        """Get the name of the currently active agent for display purposes."""
        return self._current_agent.__name__.replace("Agent", "").lower()
