from byte import ServiceProvider
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
