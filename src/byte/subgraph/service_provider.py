from typing import List, Type

from byte import ServiceProvider
from byte.node import Node
from byte.subgraph import (
    AskAgent,
    CoderAgent,
    CommitAgent,
)


class SubgraphServiceProvider(ServiceProvider):
    """ """

    def sub_graphs(self) -> List[Type[Node]]:
        return [
            # keep-sorted start
            AskAgent,
            CoderAgent,
            CommitAgent,
            # keep-sorted end
        ]

    def register(self) -> None:
        # Create all Nodes
        for sub_graph_class in self.sub_graphs():
            self.app.bind(sub_graph_class)
