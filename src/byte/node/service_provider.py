from byte import ServiceProvider
from byte.node.nodes import (
    EndNode,
    LintNode,
    RoutingNode,
    StartNode,
    ToolNode,
)


class NodeServiceProvider(ServiceProvider):
    """ """

    def nodes(self):
        return [
            # keep-sorted start
            EndNode,
            LintNode,
            RoutingNode,
            StartNode,
            ToolNode,
            # keep-sorted end
        ]
