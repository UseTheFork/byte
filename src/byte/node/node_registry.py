from typing import TYPE_CHECKING, Dict, Type

from byte.support import Str

if TYPE_CHECKING:
    from byte.node import BaseNode


class NodeRegistry:
    """ """

    def __init__(self, *args, **kwargs):
        self._nodes: Dict[str, Type[BaseNode]] = {}

    def register(self, node: Type[BaseNode]):
        """ """
        node_str = Str.class_to_snake_case(node)
        self._nodes[node_str] = node

    def all(self):
        """ """
        return self._nodes
