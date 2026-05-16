from byte import ServiceProvider
from byte.orchestration import (
    CompleteSimpleTurnTool,
    CompleteTurnTool,
    CreateAnalysisTool,
    CreatePlanTool,
    WorkflowService,
)


class OrchestrationServiceProvider(ServiceProvider):
    """ """

    def tools(self):
        return [
            # keep-sorted start
            # CompletePlanStepTool,
            CompleteSimpleTurnTool,
            CompleteTurnTool,
            CreateAnalysisTool,
            CreatePlanTool,
            # keep-sorted end
        ]

    def services(self):
        return [
            # keep-sorted start
            WorkflowService,
            # keep-sorted end
        ]
