"""Agent domain for AI agent implementations and orchestration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.domain.agent.implementations.ask.agent import AskAgent
    from byte.domain.agent.implementations.ask.command import AskCommand
    from byte.domain.agent.implementations.base import Agent
    from byte.domain.agent.implementations.cleaner.agent import CleanerAgent
    from byte.domain.agent.implementations.coder.agent import CoderAgent
    from byte.domain.agent.implementations.commit.agent import CommitAgent, CommitPlanAgent
    from byte.domain.agent.implementations.conventions.agent import ConventionAgent
    from byte.domain.agent.implementations.conventions.command import ConventionCommand
    from byte.domain.agent.implementations.copy.agent import CopyAgent
    from byte.domain.agent.implementations.research.agent import ResearchAgent
    from byte.domain.agent.implementations.research.command import ResearchCommand
    from byte.domain.agent.implementations.show.agent import ShowAgent
    from byte.domain.agent.implementations.show.command import ShowCommand
    from byte.domain.agent.implementations.subprocess.agent import SubprocessAgent
    from byte.domain.agent.nodes.assistant_node import AssistantNode
    from byte.domain.agent.nodes.base_node import Node
    from byte.domain.agent.nodes.copy_node import CopyNode
    from byte.domain.agent.nodes.end_node import EndNode
    from byte.domain.agent.nodes.extract_node import ExtractNode
    from byte.domain.agent.nodes.lint_node import LintNode
    from byte.domain.agent.nodes.parse_blocks_node import ParseBlocksNode
    from byte.domain.agent.nodes.show_node import ShowNode
    from byte.domain.agent.nodes.start_node import StartNode
    from byte.domain.agent.nodes.subprocess_node import SubprocessNode
    from byte.domain.agent.nodes.tool_node import ToolNode
    from byte.domain.agent.nodes.validation_node import ValidationNode
    from byte.domain.agent.schemas import AssistantContextSchema, ConstraintSchema, MetadataSchema, TokenUsageSchema
    from byte.domain.agent.service.agent_service import AgentService

__all__ = (
    "Agent",
    "AgentService",
    "AskAgent",
    "AskCommand",
    "AssistantContextSchema",
    "AssistantNode",
    "CleanerAgent",
    "CoderAgent",
    "CommitAgent",
    "CommitPlanAgent",
    "ConstraintSchema",
    "ConventionAgent",
    "ConventionCommand",
    "CopyAgent",
    "CopyNode",
    "EndNode",
    "ExtractNode",
    "LintNode",
    "MetadataSchema",
    "Node",
    "ParseBlocksNode",
    "ResearchAgent",
    "ResearchCommand",
    "ShowAgent",
    "ShowCommand",
    "ShowNode",
    "StartNode",
    "SubprocessAgent",
    "SubprocessNode",
    "TokenUsageSchema",
    "ToolNode",
    "ValidationNode",
)

_dynamic_imports = {
    # keep-sorted start
    "Agent": "implementations.base",
    "AgentService": "service.agent_service",
    "AskAgent": "implementations.ask.agent",
    "AskCommand": "implementations.ask.command",
    "AssistantContextSchema": "schemas",
    "AssistantNode": "nodes.assistant_node",
    "CleanerAgent": "implementations.cleaner.agent",
    "CoderAgent": "implementations.coder.agent",
    "CommitAgent": "implementations.commit.agent",
    "CommitPlanAgent": "implementations.commit.agent",
    "ConstraintSchema": "schemas",
    "ConventionAgent": "implementations.conventions.agent",
    "ConventionCommand": "implementations.conventions.command",
    "CopyAgent": "implementations.copy.agent",
    "CopyNode": "nodes.copy_node",
    "EndNode": "nodes.end_node",
    "ExtractNode": "nodes.extract_node",
    "LintNode": "nodes.lint_node",
    "MetadataSchema": "schemas",
    "Node": "nodes.base_node",
    "ParseBlocksNode": "nodes.parse_blocks_node",
    "ResearchAgent": "implementations.research.agent",
    "ResearchCommand": "implementations.research.command",
    "ShowAgent": "implementations.show.agent",
    "ShowCommand": "implementations.show.command",
    "ShowNode": "nodes.show_node",
    "StartNode": "nodes.start_node",
    "SubprocessAgent": "implementations.subprocess.agent",
    "SubprocessNode": "nodes.subprocess_node",
    "TokenUsageSchema": "schemas",
    "ToolNode": "nodes.tool_node",
    "ValidationNode": "nodes.validation_node",
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
