from abc import ABC, abstractmethod
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState
from byte.support import Str
from byte.support.mixins import Bootable, Eventable


class Node(ABC, Bootable, Eventable):
    def get_node_name(self) -> str:
        """Get the snake_case name of the node based on its class name.

        Usage: `node_name = node.get_node_name()` -> "main_model_node"
        """
        return Str.class_to_snake_case(self.__class__.__name__)

    def route_to(self, goto: str, update: dict | None = None) -> Command:
        """Route to a target node through the routing node.

        Usage: `return self.route_to("lint_node", {"parsed_blocks": blocks})`
        """
        if update is None:
            update = {}

        routing_state = {"target": goto, "source": self.get_node_name()}

        return Command(goto="routing_node", update={**update, "routing": routing_state})

    @abstractmethod
    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Any:
        """Execute the node logic. Must be implemented by subclasses."""
