from typing import List, Type

from byte import ServiceProvider
from byte.node import (
    EndNode,
    ExtractNode,
    LintNode,
    ModelMainNode,
    ModelReasoningNode,
    ModelWeakNode,
    Node,
    ParseBlocksNode,
    RoutingNode,
    StartNode,
    ToolNode,
    ValidationNode,
)


class NodeServiceProvider(ServiceProvider):
    """ """

    def nodes(self) -> List[Type[Node]]:
        return [
            # keep-sorted start
            EndNode,
            ExtractNode,
            LintNode,
            ModelMainNode,
            ModelReasoningNode,
            ModelWeakNode,
            ParseBlocksNode,
            RoutingNode,
            StartNode,
            ToolNode,
            ValidationNode,
            # keep-sorted end
        ]

    def register(self) -> None:
        # Create all Nodes
        for node_class in self.nodes():
            self.app.bind(node_class)
