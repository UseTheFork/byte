from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AgentSession:
    current_agent: str = "coder"  # Default agent
    thread_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


# In CommandProcessor
class CommandProcessor:
    def __init__(self, container):
        self.container = container
        self._current_agent = "coder"  # Default to coder agent

    async def _process_regular_input(self, user_input: str) -> None:
        """Route regular input to the currently active agent."""
        agent_service = await self.container.make("agent_service")
        await agent_service.route_to_agent(self._current_agent, user_input)

    def set_active_agent(self, agent_name: str) -> None:
        """Switch the active agent for regular input processing."""
        self._current_agent = agent_name
