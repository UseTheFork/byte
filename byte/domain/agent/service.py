from typing import TYPE_CHECKING, Optional

from byte.core.config.configurable import Configurable
from byte.core.events.eventable import Eventable
from byte.core.mixins.bootable import Bootable

if TYPE_CHECKING:
    from byte.container import Container


# byte/domain/agent/service.py
class AgentService(Bootable, Configurable, Eventable):
    """Main agent service that routes requests to specialized agents."""

    def __init__(self, container: Optional["Container"] = None):
        self.container = container
        self._current_agent = "coder"  # Default
        self._agents = {}

    async def route_to_agent(self, agent_name: str, request: str):
        """Route request to the specified agent."""
        if agent_name not in self._agents:
            # Lazy load agent
            agent_service = await self.container.make(f"{agent_name}_service")
            self._agents[agent_name] = agent_service

        agent = self._agents[agent_name]

        # Return the async generator directly, don't await it
        async for event in agent.stream_code(request):
            yield event

    def set_active_agent(self, agent_name: str) -> bool:
        """Switch the active agent."""
        # Validate agent exists
        if self._is_valid_agent(agent_name):
            self._current_agent = agent_name
            return True
        return False

    def _is_valid_agent(self, agent_name: str) -> bool:
        """Check if the agent name is valid."""
        valid_agents = ["coder"]  # Add more agents as they're implemented
        return agent_name in valid_agents

    def get_active_agent(self) -> str:
        return self._current_agent
