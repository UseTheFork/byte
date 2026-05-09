from typing import List, Type

from byte import Command, Service, ServiceProvider
from byte.workflow import (
    AskCommand,
    AskWorkflow,
    BaseWorkflow,
    CoderCommand,
    CoderWorkflow,
    WorkflowService,
)


class WorkflowServiceProvider(ServiceProvider):
    """ """

    def services(self) -> List[Type[Service]]:
        return [
            # keep-sorted start
            WorkflowService,
            # keep-sorted end
        ]

    def workflows(self) -> List[Type[BaseWorkflow]]:
        return [
            # keep-sorted start
            AskWorkflow,
            CoderWorkflow,
            # keep-sorted end
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            # keep-sorted start
            AskCommand,
            CoderCommand,
            # keep-sorted end
        ]
