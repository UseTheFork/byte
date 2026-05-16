from byte import ServiceProvider
from byte.plan import CompletePlanStepTool, ConfirmCompletePlanStepTool


class PlanServiceProvider(ServiceProvider):
    def tools(self):
        return [
            # keep-sorted start
            CompletePlanStepTool,
            ConfirmCompletePlanStepTool,
            # keep-sorted end
        ]
