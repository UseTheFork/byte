from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.plan.models import PlanStep
    from byte.plan.service_provider import PlanServiceProvider
    from byte.plan.tools.complete_plan_step_tool import CompletePlanStepTool
    from byte.plan.tools.complete_turn_tool import CompleteTurnTool
    from byte.plan.tools.confirm_complete_plan_step_tool import ConfirmCompletePlanStepTool
    from byte.plan.tools.create_plan_tool import CreatePlanTool


__all__ = (
    "CompletePlanStepTool",
    "CompleteTurnTool",
    "ConfirmCompletePlanStepTool",
    "CreatePlanTool",
    "PlanServiceProvider",
    "PlanStep",
)

_dynamic_imports = {
    # keep-sorted start
    "CompletePlanStepTool": "tools.complete_plan_step_tool",
    "CompleteTurnTool": "tools.complete_turn_tool",
    "ConfirmCompletePlanStepTool": "tools.confirm_complete_plan_step_tool",
    "CreatePlanTool": "tools.create_plan_tool",
    "PlanServiceProvider": "service_provider",
    "PlanStep": "models",
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
