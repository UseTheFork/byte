from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar

from langgraph.graph import StateGraph

from byte.node import BaseNode
from byte.node.nodes import DummyNode, EndNode, RoutingNode, StartNode
from byte.orchestration import (
    AssistantContextSchema,
    BaseState,
)
from byte.support import Str

if TYPE_CHECKING:
    from byte.foundation import Application

T = TypeVar("T")


class GraphBuilder:
    def __init__(self, app: Application, start_node: Type[BaseNode] = DummyNode, **kwargs):
        if app is None:
            raise ValueError("app parameter is required")
        self.app = app
        self._nodes = {}

        # Discover all available Node classes from the agent module.
        self._dummy_nodes = self.discover_node_classes()

        self.add_node(StartNode, goto=start_node)
        self.add_node(RoutingNode)
        self.add_node(EndNode)

    def discover_node_classes(self) -> dict[str, Type]:
        """Discover all classes that extend the base Node class.

        Uses the NodeServiceProvider to get all registered node and agent classes.

        Returns:
            Dictionary mapping node class names to their types

        Usage: Called internally during GraphBuilder initialization
        """
        from byte.node import NodeServiceProvider

        node_service_provider = self.app.make(NodeServiceProvider)
        node_classes = {}

        # Get nodes from the service provider
        for node_class in node_service_provider.nodes():
            node_string = Str.class_to_snake_case(node_class.__name__)
            node_classes[node_string] = node_class

        # Get agents from the service provider
        for agent_class in node_service_provider.agents():
            agent_string = Str.class_to_snake_case(agent_class.__name__)
            node_classes[agent_string] = agent_class

        return node_classes

    def add_node(self, node: Type[BaseNode], **kwargs):
        """Add a node to the graph builder.

        Creates an instance of the node class using the app container and stores
        it by the node's class name for later use in graph construction.

        Args:
            node_class: The Node subclass to instantiate
            **kwargs: Additional keyword arguments passed to the node constructor

        Returns:
            The instantiated node instance

        Usage: `builder.add_node(AssistantNode, goto="parse_blocks_node")`
        """
        node_instance = self.app.make(node, **kwargs)
        node_name = Str.class_to_snake_case(node)

        self._nodes[node_name] = node_instance

        # Remove from dummy nodes since it's now been added
        if node_name in self._dummy_nodes:
            del self._dummy_nodes[node_name]

        return node_instance

    def build(self, checkpointer=None) -> StateGraph:
        """Build and compile the state graph with all registered nodes.

        Creates a StateGraph with BaseState and AssistantContextSchema, adds all
        registered nodes and dummy nodes, then sets up entry and finish points.

        Args:
            checkpointer: Optional checkpointer for state persistence

        Returns:
            Configured StateGraph ready for compilation

        Usage: `graph = builder.build()` -> returns configured state graph
        """
        graph = StateGraph(BaseState, context_schema=AssistantContextSchema)  # ty:ignore[invalid-argument-type]

        for node_name, node_instance in self._nodes.items():
            graph.add_node(node_name, node_instance)

        for node_name, node_class in self._dummy_nodes.items():
            graph.add_node(node_name, self.app.make(DummyNode))

        # Define entry edges
        graph.set_entry_point("start_node")
        graph.set_finish_point("end_node")

        return graph
