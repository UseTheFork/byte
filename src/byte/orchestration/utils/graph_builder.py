from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar

from langgraph.graph import StateGraph

from byte.node import BaseNode, NodeRegistry
from byte.node.nodes import DummyNode, EndNode, RoutingNode, StartNode, ToolNode
from byte.orchestration import (
    AssistantContextSchema,
    BaseState,
)
from byte.support import Str

if TYPE_CHECKING:
    from byte.foundation import Application

T = TypeVar("T")


class GraphBuilder:
    """Build and configure state graphs for workflow execution."""

    def __init__(self, app: Application, start_node: Type[BaseNode] = DummyNode, **kwargs) -> None:
        """Initialize the graph builder with application context and initial nodes."""
        if app is None:
            raise ValueError("app parameter is required")
        self.app = app
        self._nodes = {}

        # Discover all available Node classes from the agent module.
        self._dummy_nodes = self.discover_node_classes()

        self.add_node(StartNode, goto=start_node)
        self.add_node(ToolNode)
        self.add_node(RoutingNode)
        self.add_node(EndNode)

    def discover_node_classes(self) -> dict[str, Type]:
        """Discover all available node classes from the node registry."""
        node_registry = self.app.make(NodeRegistry)

        return node_registry.all()

    def add_node(self, node: Type[BaseNode], **kwargs):
        """Add a node to the graph and register it for later use."""
        node_instance = self.app.make(node, **kwargs)
        node_name = Str.class_to_snake_case(node)

        self._nodes[node_name] = node_instance

        # Remove from dummy nodes since it's now been added
        if node_name in self._dummy_nodes:
            del self._dummy_nodes[node_name]

        return node_instance

    def build(self, checkpointer=None) -> StateGraph:
        """Build and compile the state graph with all registered nodes and entry/finish points."""
        graph = StateGraph(BaseState, context_schema=AssistantContextSchema)  # ty:ignore[invalid-argument-type]

        for node_name, node_instance in self._nodes.items():
            graph.add_node(node_name, node_instance)

        for node_name, node_class in self._dummy_nodes.items():
            graph.add_node(node_name, self.app.make(DummyNode))

        # Define entry edges
        graph.set_entry_point("start_node")
        graph.set_finish_point("end_node")

        return graph
