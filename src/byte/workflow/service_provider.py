from byte import ServiceProvider
from byte.workflow import (
    AskCommand,
    AskWorkflow,
    CoderCommand,
    CoderWorkflow,
    WorkflowService,
)


class WorkflowServiceProvider(ServiceProvider):
    """ """

    def services(self):
        return [
            # keep-sorted start
            WorkflowService,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            AskWorkflow,
            CoderWorkflow,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            AskCommand,
            CoderCommand,
            # keep-sorted end
        ]
