from typing import List, Type

from byte import ServiceProvider
from byte.node import (
    AssistantNode,
    EndNode,
    ExtractNode,
    LintNode,
    MainModelNode,
    Node,
    ParseBlocksNode,
    ReasoningModelNode,
    RoutingNode,
    StartNode,
    ToolNode,
    ValidationNode,
    WeakModelNode,
)


class NodeServiceProvider(ServiceProvider):
    """ """

    def nodes(self) -> List[Type[Node]]:
        return [
            # keep-sorted start
            AssistantNode,
            EndNode,
            ExtractNode,
            LintNode,
            MainModelNode,
            ParseBlocksNode,
            ReasoningModelNode,
            RoutingNode,
            StartNode,
            ToolNode,
            ValidationNode,
            WeakModelNode,
            # keep-sorted end
        ]

    def register(self) -> None:
        # Create all Nodes
        for node_class in self.nodes():
            self.app.bind(node_class)
