from typing import TYPE_CHECKING

from byte.context import make
from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable
from byte.domain.events.mixins import Eventable

if TYPE_CHECKING:
    pass


class AgentService(Bootable, Configurable, Eventable):
    """Main agent service that routes requests to specialized agents."""

    _current_agent: str = "coder"

    async def boot(self):
        """Boot method to initialize the agent service."""
        self._current_agent = "coder"  # Set default agent
        self._agents = {}

    async def route_to_agent(self, agent_name: str, request: str):
        """Route request to the specified agent."""
        if agent_name not in self._agents:
            # Lazy load agent
            agent_service = await make(f"{agent_name}_service")
            self._agents[agent_name] = agent_service

        agent = self._agents[agent_name]

        # Return the async generator directly, don't await it
        async for event in agent.stream(request):
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
        """Get the currently active agent, ensuring service is booted."""
        return self._current_agent
