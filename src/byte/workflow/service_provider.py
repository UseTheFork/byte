from byte import ServiceProvider
from byte.workflow import (
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
