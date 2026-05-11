"""Node implementations for the Byte framework."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.node.base_agent_node import BaseAgentNode
    from byte.node.base_node import BaseNode
    from byte.node.events import NodeEvents
    from byte.node.node_registry import NodeRegistry
    from byte.node.service_provider import NodeServiceProvider

__all__ = (
    "BaseAgentNode",
    "BaseNode",
    "NodeEvents",
    "NodeRegistry",
    "NodeServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "BaseAgentNode": "base_agent_node",
    "BaseNode": "base_node",
    "NodeEvents": "events",
    "NodeServiceProvider": "service_provider",
    "NodeRegistry": "node_registry",
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
