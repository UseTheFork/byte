from byte import ServiceProvider
from byte.orchestration import (
    CompleteSimpleTurnTool,
    CompleteTurnTool,
    CreateAnalysisTool,
    CreatePlanTool,
    UpdatePhaseTool,
    UserConfirmPhaseTool,
    WorkflowService,
)


class OrchestrationServiceProvider(ServiceProvider):
    """ """

    def tools(self):
        return [
            # keep-sorted start
            CompleteSimpleTurnTool,
            CompleteTurnTool,
            CreateAnalysisTool,
            CreatePlanTool,
            UpdatePhaseTool,
            UserConfirmPhaseTool,
            # keep-sorted end
        ]

    def services(self):
        return [
            # keep-sorted start
            WorkflowService,
            # keep-sorted end
        ]
