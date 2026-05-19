"""Nodes."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.node.nodes.dummy_node import DummyNode
    from byte.node.nodes.end_node import EndNode
    from byte.node.nodes.routing_node import RoutingNode
    from byte.node.nodes.start_node import StartNode
    from byte.node.nodes.tool_node import ToolNode

__all__ = (
    "DummyNode",
    "EndNode",
    "RoutingNode",
    "StartNode",
    "ToolNode",
)

_dynamic_imports = {
    # keep-sorted start
    "DummyNode": "dummy_node",
    "EndNode": "end_node",
    "RoutingNode": "routing_node",
    "StartNode": "start_node",
    "ToolNode": "tool_node",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
