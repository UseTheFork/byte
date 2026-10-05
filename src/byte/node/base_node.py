from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from byte.support import Str
from byte.support.mixins import Bootable, Eventable

if TYPE_CHECKING:
    from byte.orchestration import BaseState


class BaseNode(ABC, Bootable, Eventable):
    def get_node_name(self) -> str:
        """Get the snake_case name of the node based on its class name."""
        return Str.class_to_snake_case(self.__class__.__name__)

    def get_node_config(self) -> dict[str, Any]:
        """Return node configuration for graph builder."""
        return {}

    def route_to(self, goto: str, update: dict | None = None) -> Command:
        """Route to a target node through the routing node."""
        if update is None:
            update = {}

        routing_state = {"target": goto, "source": self.get_node_name()}

        return Command(goto="routing_node", update={**update, "routing": routing_state})

    def route_back(self, state: BaseState, update: dict | None = None) -> Command:
        """Route back to the previous node that called this node."""
        source = state.get("routing", {}).get("source", "end_node")
        return self.route_to(source, update)

    @abstractmethod
    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Any:
        """Execute the node logic."""
        ...
