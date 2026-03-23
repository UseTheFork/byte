"""Agent domain for AI agent implementations and orchestration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.agent.command.config_agent_command import ConfigAgentCommand
    from byte.agent.exceptions import DummyNodeReachedException
    from byte.agent.implementations.ask.agent import AskAgent
    from byte.agent.implementations.base import Agent
    from byte.agent.implementations.cleaner.agent import CleanerAgent
    from byte.agent.implementations.coder.agent import CoderAgent
    from byte.agent.implementations.commit.agent import CommitAgent, CommitPlanAgent
    from byte.agent.implementations.conventions.agent import ConventionAgent
    from byte.agent.implementations.research.agent import ResearchAgent
    from byte.agent.implementations.research.command import ResearchCommand
    from byte.agent.nodes.agents.ask.ask_agent_node import AskAgentNode
    from byte.agent.nodes.agents.base_agent_node import BaseAgentNode
    from byte.agent.nodes.agents.code_reviewer.code_reviewer_agent_node import CodeReviewerAgentNode
    from byte.agent.nodes.assistant_node import AssistantNode
    from byte.agent.nodes.base_node import Node
    from byte.agent.nodes.dummy_node import DummyNode
    from byte.agent.nodes.end_node import EndNode
    from byte.agent.nodes.extract_node import ExtractNode, SessionContextFormatter
    from byte.agent.nodes.lint_node import LintNode
    from byte.agent.nodes.model.main_model_node import MainModelNode
    from byte.agent.nodes.model.reasoning_model_node import ReasoningModelNode
    from byte.agent.nodes.model.weak_model_node import WeakModelNode
    from byte.agent.nodes.parse_blocks_node import ParseBlocksNode
    from byte.agent.nodes.routing_node import RoutingNode
    from byte.agent.nodes.show_node import ShowNode
    from byte.agent.nodes.start_node import StartNode
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
    from byte.agent.validators.user_confirm_validator import UserConfirmValidator

__all__ = (
    "Agent",
    "AgentConfigBoolSchema",
    "AgentConfigStringSchema",
    "AgentService",
    "AgentServiceProvider",
    "AgentSettingsService",
    "AskAgent",
    "AskAgentNode",
    "AssistantContextSchema",
    "AssistantNode",
    "BaseAgentNode",
    "BaseState",
    "CleanerAgent",
    "CodeReviewerAgentNode",
    "CoderAgent",
    "CommitAgent",
    "CommitPlanAgent",
    "ConfigAgentCommand",
    "ConstraintSchema",
    "ConventionAgent",
    "DummyNode",
    "DummyNodeReachedException",
    "EndNode",
    "ExtractNode",
    "LintNode",
    "MainModelNode",
    "MaxLinesValidator",
    "MetadataSchema",
    "Node",
    "ParseBlocksNode",
    "PromptSettingsSchema",
    "ReasoningModelNode",
    "ResearchAgent",
    "ResearchCommand",
    "RoutingNode",
    "SessionContextFormatter",
    "ShowNode",
    "StartNode",
    "TokenUsageSchema",
    "ToolNode",
    "UserConfirmValidator",
    "ValidationError",
    "ValidationNode",
    "Validator",
    "WeakModelNode",
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
    "AskAgentNode": "nodes.agents.ask.ask_agent_node",
    "AssistantContextSchema": "schemas",
    "AssistantNode": "nodes.assistant_node",
    "BaseAgentNode": "nodes.agents.base_agent_node",
    "BaseState": "state",
    "CleanerAgent": "implementations.cleaner.agent",
    "CodeReviewerAgentNode": "nodes.agents.code_reviewer.code_reviewer_agent_node",
    "CoderAgent": "implementations.coder.agent",
    "CommitAgent": "implementations.commit.agent",
    "CommitPlanAgent": "implementations.commit.agent",
    "ConfigAgentCommand": "command.config_agent_command",
    "ConstraintSchema": "schemas",
    "ConventionAgent": "implementations.conventions.agent",
    "DummyNode": "nodes.dummy_node",
    "DummyNodeReachedException": "exceptions",
    "EndNode": "nodes.end_node",
    "ExtractNode": "nodes.extract_node",
    "LintNode": "nodes.lint_node",
    "MainModelNode": "nodes.model.main_model_node",
    "MaxLinesValidator": "validators.max_lines",
    "MetadataSchema": "schemas",
    "Node": "nodes.base_node",
    "ParseBlocksNode": "nodes.parse_blocks_node",
    "PromptSettingsSchema": "schemas",
    "ReasoningModelNode": "nodes.model.reasoning_model_node",
    "ResearchAgent": "implementations.research.agent",
    "ResearchCommand": "implementations.research.command",
    "RoutingNode": "nodes.routing_node",
    "SessionContextFormatter": "nodes.extract_node",
    "ShowNode": "nodes.show_node",
    "StartNode": "nodes.start_node",
    "TokenUsageSchema": "schemas",
    "ToolNode": "nodes.tool_node",
    "UserConfirmValidator": "validators.user_confirm_validator",
    "ValidationError": "validators.base",
    "ValidationNode": "nodes.validation_node",
    "Validator": "validators.base",
    "WeakModelNode": "nodes.model.weak_model_node",
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
