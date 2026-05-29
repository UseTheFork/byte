"""Agent domain for AI agent implementations and orchestration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.orchestration.base_workflow import BaseWorkflow
    from byte.orchestration.events import OrchestrationEvents
    from byte.orchestration.exceptions import ByteAgentException, DummyNodeReachedException
    from byte.orchestration.leaves.leaf import Leaf
    from byte.orchestration.leaves.leaves import Leaves
    from byte.orchestration.message_fragments.message_fragment import MessageFragment
    from byte.orchestration.message_fragments.message_fragments import MessageFragments
    from byte.orchestration.messages import AIMessage
    from byte.orchestration.models.phase_model import PhaseModel
    from byte.orchestration.models.route_phase_model import RoutePhaseModel
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
    from byte.orchestration.service_provider import OrchestrationServiceProvider
    from byte.orchestration.services.workflow_service import WorkflowService
    from byte.orchestration.state import BaseState, RoutingState
    from byte.orchestration.tools.complete_simple_turn_tool import CompleteSimpleTurnTool
    from byte.orchestration.tools.complete_turn_tool import CompleteTurnTool
    from byte.orchestration.tools.create_analysis_tool import CreateAnalysisTool
    from byte.orchestration.tools.create_plan_tool import CreatePlanTool
    from byte.orchestration.tools.update_phase_tool import UpdatePhaseTool
    from byte.orchestration.tools.user_confirm_phase_tool import UserConfirmPhaseTool
    from byte.orchestration.utils.graph_builder import GraphBuilder
    from byte.orchestration.utils.harness_state_utils import HarnessStateUtils
    from byte.orchestration.utils.phase_utils import PhaseUtils
    from byte.orchestration.utils.prompt_assembler import PromptAssembler
    from byte.orchestration.utils.reducer import Reducer


__all__ = (
    "AIMessage",
    "AgentConfigBoolSchema",
    "AgentConfigSchema",
    "AgentConfigStringSchema",
    "AssistantContextSchema",
    "BaseState",
    "BaseWorkflow",
    "ByteAgentException",
    "CompleteSimpleTurnTool",
    "CompleteTurnTool",
    "ConstraintSchema",
    "CreateAnalysisTool",
    "CreatePlanTool",
    "DummyNodeReachedException",
    "GraphBuilder",
    "HarnessStateUtils",
    "Leaf",
    "Leaves",
    "MessageFragment",
    "MessageFragments",
    "MetadataSchema",
    "OrchestrationEvents",
    "OrchestrationServiceProvider",
    "PhaseModel",
    "PhaseUtils",
    "PromptAssembler",
    "PromptSettingsSchema",
    "Reducer",
    "RoutePhaseModel",
    "RoutingState",
    "TokenUsageSchema",
    "UpdatePhaseTool",
    "UserConfirmPhaseTool",
    "WorkflowService",
)


_dynamic_imports = {
    # keep-sorted start
    "AIMessage": "messages",
    "AgentConfigBoolSchema": "schemas",
    "AgentConfigSchema": "schemas",
    "AgentConfigStringSchema": "schemas",
    "AssistantContextSchema": "schemas",
    "BaseState": "state",
    "BaseWorkflow": "base_workflow",
    "ByteAgentException": "exceptions",
    "CompleteSimpleTurnTool": "tools.complete_simple_turn_tool",
    "CompleteTurnTool": "tools.complete_turn_tool",
    "ConstraintSchema": "schemas",
    "CreateAnalysisTool": "tools.create_analysis_tool",
    "CreatePlanTool": "tools.create_plan_tool",
    "DummyNodeReachedException": "exceptions",
    "GraphBuilder": "utils.graph_builder",
    "HarnessStateUtils": "utils.harness_state_utils",
    "Leaf": "leaves.leaf",
    "Leaves": "leaves.leaves",
    "MessageFragment": "message_fragments.message_fragment",
    "MessageFragments": "message_fragments.message_fragments",
    "MetadataSchema": "schemas",
    "OrchestrationEvents": "events",
    "OrchestrationServiceProvider": "service_provider",
    "PhaseModel": "models.phase_model",
    "PhaseUtils": "utils.phase_utils",
    "PromptAssembler": "utils.prompt_assembler",
    "PromptSettingsSchema": "schemas",
    "Reducer": "utils.reducer",
    "RoutePhaseModel": "models.route_phase_model",
    "RoutingState": "state",
    "TokenUsageSchema": "schemas",
    "UpdatePhaseTool": "tools.update_phase_tool",
    "UserConfirmPhaseTool": "tools.user_confirm_phase_tool",
    "WorkflowService": "services.workflow_service",
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
