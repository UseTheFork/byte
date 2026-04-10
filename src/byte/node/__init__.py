"""Agent domain for AI agent implementations and orchestration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.node.agents.commit_agent_node import CommitAgentNode
    from byte.node.base_agent_node import BaseAgentNode
    from byte.node.base_node import Node, Node as BaseNode
    from byte.node.events import NodeEvents
    from byte.node.implementations.dummy_node import DummyNode
    from byte.node.implementations.end_node import EndNode
    from byte.node.implementations.extract_node import ExtractNode
    from byte.node.implementations.lint_node import LintNode
    from byte.node.implementations.model_base_node import ModelBaseNode
    from byte.node.implementations.model_main_node import ModelMainNode
    from byte.node.implementations.model_reasoning_node import ModelReasoningNode
    from byte.node.implementations.model_weak_node import ModelWeakNode
    from byte.node.implementations.parse_blocks_node import ParseBlocksNode
    from byte.node.implementations.routing_node import RoutingNode
    from byte.node.implementations.start_node import StartNode
    from byte.node.implementations.tool_node import ToolNode
    from byte.node.implementations.validation_node import ValidationNode
    from byte.node.service_provider import NodeServiceProvider

__all__ = (
    "BaseAgentNode",
    "BaseNode",
    "CommitAgentNode",
    "DummyNode",
    "EndNode",
    "ExtractNode",
    "LintNode",
    "ModelBaseNode",
    "ModelMainNode",
    "ModelReasoningNode",
    "ModelWeakNode",
    "Node",
    "NodeEvents",
    "NodeServiceProvider",
    "ParseBlocksNode",
    "RoutingNode",
    "StartNode",
    "ToolNode",
    "ValidationNode",
)

_dynamic_imports = {
    # keep-sorted start
    "BaseAgentNode": "base_agent_node",
    "BaseNode": "base_node",
    "DummyNode": "implementations.dummy_node",
    "EndNode": "implementations.end_node",
    "CommitAgentNode": "agents.commit_agent_node",
    "ExtractNode": "implementations.extract_node",
    "LintNode": "implementations.lint_node",
    "ModelBaseNode": "implementations.model_base_node",
    "ModelMainNode": "implementations.model_main_node",
    "ModelReasoningNode": "implementations.model_reasoning_node",
    "ModelWeakNode": "implementations.model_weak_node",
    "Node": "base_node",
    "NodeEvents": "events",
    "NodeServiceProvider": "service_provider",
    "ParseBlocksNode": "implementations.parse_blocks_node",
    "RoutingNode": "implementations.routing_node",
    "StartNode": "implementations.start_node",
    "ToolNode": "implementations.tool_node",
    "ValidationNode": "implementations.validation_node",
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
