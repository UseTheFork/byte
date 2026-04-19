from typing import List, Type

from byte import ServiceProvider
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.agents import AskAgentNode, CoderAgentNode, CommitAgentNode
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

    def agents(self) -> List[Type[BaseAgentNode]]:
        return [
            # keep-sorted start
            AskAgentNode,
            CoderAgentNode,
            CommitAgentNode,
            # keep-sorted end
        ]

    def nodes(self) -> List[Type[BaseNode]]:
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

        for agent_class in self.agents():
            self.app.bind(agent_class)
