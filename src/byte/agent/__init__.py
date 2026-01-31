"""Agent domain for AI agent implementations and orchestration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.agent.command.config_agent_command import ConfigAgentCommand
    from byte.agent.exceptions import DummyNodeReachedException
    from byte.agent.implementations.ask.agent import AskAgent
    from byte.agent.implementations.ask.command import AskCommand
    from byte.agent.implementations.base import Agent
    from byte.agent.implementations.cleaner.agent import CleanerAgent
    from byte.agent.implementations.coder.agent import CoderAgent
    from byte.agent.implementations.commit.agent import CommitAgent, CommitPlanAgent
    from byte.agent.implementations.conventions.agent import ConventionAgent
    from byte.agent.implementations.conventions.command import ConventionCommand
    from byte.agent.implementations.research.agent import ResearchAgent
    from byte.agent.implementations.research.command import ResearchCommand
    from byte.agent.implementations.show.agent import ShowAgent
    from byte.agent.implementations.show.command import ShowCommand
    from byte.agent.implementations.subprocess.agent import SubprocessAgent
    from byte.agent.nodes.assistant_node import AssistantNode
    from byte.agent.nodes.base_node import Node
    from byte.agent.nodes.dummy_node import DummyNode
    from byte.agent.nodes.end_node import EndNode
    from byte.agent.nodes.extract_node import ExtractNode, SessionContextFormatter
    from byte.agent.nodes.lint_node import LintNode
    from byte.agent.nodes.parse_blocks_node import ParseBlocksNode
    from byte.agent.nodes.show_node import ShowNode
    from byte.agent.nodes.start_node import StartNode
    from byte.agent.nodes.subprocess_node import SubprocessNode
    from byte.agent.nodes.tool_node import ToolNode
    from byte.agent.nodes.validation_node import ValidationNode
    from byte.agent.reducers import add_constraints, replace_list, replace_str, update_metadata
    from byte.agent.schemas import (
        AgentConfigBoolSchema,
        AgentConfigStringSchema,
        AssistantContextSchema,
        ConstraintSchema,
        MetadataSchema,
        PromptSettingsSchema,
        TokenUsageSchema,
    )
    from byte.agent.service.agent_service import AgentService
    from byte.agent.service.agent_settings_service import AgentSettingsService
    from byte.agent.service_provider import AgentServiceProvider
    from byte.agent.state import BaseState
    from byte.agent.validators.base import ValidationError, Validator
    from byte.agent.validators.max_lines import MaxLinesValidator

__all__ = (
    "Agent",
    "AgentConfigBoolSchema",
    "AgentConfigStringSchema",
    "AgentService",
    "AgentServiceProvider",
    "AgentSettingsService",
    "AskAgent",
    "AskCommand",
    "AssistantContextSchema",
    "AssistantNode",
    "BaseState",
    "CleanerAgent",
    "CoderAgent",
    "CommitAgent",
    "CommitPlanAgent",
    "ConfigAgentCommand",
    "ConstraintSchema",
    "ConventionAgent",
    "ConventionCommand",
    "DummyNode",
    "DummyNodeReachedException",
    "EndNode",
    "ExtractNode",
    "LintNode",
    "MaxLinesValidator",
    "MetadataSchema",
    "Node",
    "ParseBlocksNode",
    "PromptSettingsSchema",
    "ResearchAgent",
    "ResearchCommand",
    "SessionContextFormatter",
    "ShowAgent",
    "ShowCommand",
    "ShowNode",
    "StartNode",
    "SubprocessAgent",
    "SubprocessNode",
    "TokenUsageSchema",
    "ToolNode",
    "ValidationError",
    "ValidationNode",
    "Validator",
    "add_constraints",
    "replace_list",
    "replace_str",
    "update_metadata",
    "update_metadata",
)

_dynamic_imports = {
    # keep-sorted start
    "Agent": "implementations.base",
    "AgentConfigBoolSchema": "schemas",
    "AgentConfigStringSchema": "schemas",
    "AgentService": "service.agent_service",
    "AgentServiceProvider": "service_provider",
    "AgentSettingsService": "service.agent_settings_service",
    "AskAgent": "implementations.ask.agent",
    "AskCommand": "implementations.ask.command",
    "AssistantContextSchema": "schemas",
    "AssistantNode": "nodes.assistant_node",
    "BaseState": "state",
    "CleanerAgent": "implementations.cleaner.agent",
    "CoderAgent": "implementations.coder.agent",
    "CommitAgent": "implementations.commit.agent",
    "CommitPlanAgent": "implementations.commit.agent",
    "ConfigAgentCommand": "command.config_agent_command",
    "ConstraintSchema": "schemas",
    "ConventionAgent": "implementations.conventions.agent",
    "ConventionCommand": "implementations.conventions.command",
    "DummyNode": "nodes.dummy_node",
    "DummyNodeReachedException": "exceptions",
    "EndNode": "nodes.end_node",
    "ExtractNode": "nodes.extract_node",
    "LintNode": "nodes.lint_node",
    "MaxLinesValidator": "validators.max_lines",
    "MetadataSchema": "schemas",
    "Node": "nodes.base_node",
    "ParseBlocksNode": "nodes.parse_blocks_node",
    "PromptSettingsSchema": "schemas",
    "ResearchAgent": "implementations.research.agent",
    "ResearchCommand": "implementations.research.command",
    "SessionContextFormatter": "nodes.extract_node",
    "ShowAgent": "implementations.show.agent",
    "ShowCommand": "implementations.show.command",
    "ShowNode": "nodes.show_node",
    "StartNode": "nodes.start_node",
    "SubprocessAgent": "implementations.subprocess.agent",
    "SubprocessNode": "nodes.subprocess_node",
    "TokenUsageSchema": "schemas",
    "ToolNode": "nodes.tool_node",
    "ValidationError": "validators.base",
    "ValidationNode": "nodes.validation_node",
    "Validator": "validators.base",
    "add_constraints": "reducers",
    "replace_list": "reducers",
    "replace_str": "reducers",
    "update_metadata": "reducers",
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
