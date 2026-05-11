from byte import ServiceProvider
from byte.plan import CompletePlanStepTool, CompleteTurnTool, ConfirmCompletePlanStepTool, CreatePlanTool


class PlanServiceProvider(ServiceProvider):
    def tools(self):
        return [
            # keep-sorted start
            CompletePlanStepTool,
            CompleteTurnTool,
            ConfirmCompletePlanStepTool,
            CreatePlanTool,
            # keep-sorted end
        ]
