from byte import ServiceProvider
from byte.node.agents import (
    AskAgentNode,
    CoderAgentNode,
)
from byte.node.nodes import (
    EndNode,
    ExtractNode,
    LintNode,
    RoutingNode,
    StartNode,
    ToolNode,
    ValidationNode,
)


class NodeServiceProvider(ServiceProvider):
    """ """

    def agents(self):
        return [
            # keep-sorted start
            AskAgentNode,
            CoderAgentNode,
            # keep-sorted end
        ]

    def nodes(self):
        return [
            # keep-sorted start
            EndNode,
            ExtractNode,
            LintNode,
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
