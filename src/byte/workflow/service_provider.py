from typing import List, Type

from byte import Service, ServiceProvider
from byte.cli import Command
from byte.workflow import AskCommand, AskWorkflow, BaseWorkflow, CoderWorkflow, WorkflowService


class WorkflowServiceProvider(ServiceProvider):
    """ """

    def services(self) -> List[Type[Service]]:
        return [
            WorkflowService,
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
            # keep-sorted end
        ]

    def register(self) -> None:
        for workflow_class in self.workflows():
            self.app.singleton(workflow_class)
