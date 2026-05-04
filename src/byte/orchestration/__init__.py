"""Agent domain for AI agent implementations and orchestration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.orchestration.events import OrchestrationEvents
    from byte.orchestration.exceptions import ByteAgentException, DummyNodeReachedException
    from byte.orchestration.leaves.leaf import Leaf
    from byte.orchestration.leaves.leaves import Leaves
    from byte.orchestration.prompt_leaves import core_mandates
    from byte.orchestration.reducers import add_constraints, replace_list, replace_str, update_metadata
    from byte.orchestration.schemas import (
        AgentConfigBoolSchema,
        AgentConfigSchema,
        AgentConfigStringSchema,
        AssistantContextSchema,
        ConstraintSchema,
        MetadataSchema,
        PromptSettingsSchema,
        TokenUsageSchema,
    )
    from byte.orchestration.state import BaseState, PlanStep, RoutingState
    from byte.orchestration.utils.graph_builder import GraphBuilder
    from byte.orchestration.utils.prompt_assembler import PromptAssembler
    from byte.orchestration.validators.base import ValidationError, Validator
    from byte.orchestration.validators.max_lines import MaxLinesValidator
    from byte.orchestration.validators.user_confirm_validator import UserConfirmValidator

__all__ = (
    "AgentConfigBoolSchema",
    "AgentConfigSchema",
    "AgentConfigStringSchema",
    "AssistantContextSchema",
    "BaseState",
    "ByteAgentException",
    "ConstraintSchema",
    "DummyNodeReachedException",
    "GraphBuilder",
    "Leaf",
    "Leaves",
    "MaxLinesValidator",
    "MetadataSchema",
    "OrchestrationEvents",
    "PlanStep",
    "PromptAssembler",
    "PromptSettingsSchema",
    "RoutingState",
    "TokenUsageSchema",
    "UserConfirmValidator",
    "ValidationError",
    "Validator",
    "add_constraints",
    "core_mandates",
    "replace_list",
    "replace_str",
    "update_metadata",
)

_dynamic_imports = {
    # keep-sorted start
    "AgentConfigBoolSchema": "schemas",
    "AgentConfigSchema": "schemas",
    "AgentConfigStringSchema": "schemas",
    "AssistantContextSchema": "schemas",
    "BaseState": "state",
    "ByteAgentException": "exceptions",
    "ConstraintSchema": "schemas",
    "DummyNodeReachedException": "exceptions",
    "GraphBuilder": "utils.graph_builder",
    "Leaf": "leaves.leaf",
    "Leaves": "leaves.leaves",
    "MaxLinesValidator": "validators.max_lines",
    "MetadataSchema": "schemas",
    "OrchestrationEvents": "events",
    "PlanStep": "state",
    "PromptAssembler": "utils.prompt_assembler",
    "PromptSettingsSchema": "schemas",
    "RoutingState": "state",
    "TokenUsageSchema": "schemas",
    "UserConfirmValidator": "validators.user_confirm_validator",
    "ValidationError": "validators.base",
    "Validator": "validators.base",
    "add_constraints": "reducers",
    "core_mandates": "prompt_leaves",
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
