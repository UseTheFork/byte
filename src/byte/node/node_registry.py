from typing import TYPE_CHECKING, Dict, Type

from byte.support import Str
from byte.support.mixins import Bootable

if TYPE_CHECKING:
    from byte.node import BaseNode


class NodeRegistry(Bootable):
    """ """

    def boot(self, *args, **kwargs) -> None:
        self._nodes: Dict[str, Type[BaseNode]] = {}

    def register(self, node: Type[BaseNode]):
        """ """
        node_str = Str.class_to_snake_case(node)
        self._nodes[node_str] = node

    def all(self):
        """ """
        return dict(self._nodes)
