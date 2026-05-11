from byte import ServiceProvider
from byte.plan import CompletePlanStepTool, CompleteTurnTool, ConfirmCompletePlanStepTool, CreatePlanTool


class PlanServiceProvider(ServiceProvider):
    def tools(self):
        return [
            # keep-sorted start
            CreatePlanTool,
            CompletePlanStepTool,
            CompleteTurnTool,
            ConfirmCompletePlanStepTool,
            # keep-sorted end
        ]
