from byte import ServiceProvider
from byte.plan import CompletePlanStepTool, CompleteTurnTool, ConfirmCompletePlanStepTool


class PlanServiceProvider(ServiceProvider):
    def tools(self):
        return [
            # keep-sorted start
            CompletePlanStepTool,
            CompleteTurnTool,
            ConfirmCompletePlanStepTool,
            # keep-sorted end
        ]
