import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.constitution import (
    InitializeWorkflow,
)
from byte.tui import Messages
from byte.workflow import WorkflowService


class InitializeCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "init"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Initialize the project constitution",
        )
        parser.add_argument("constitution_query", nargs=argparse.REMAINDER, help="The initialization statement")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """ """

        initialize_workflow = self.app.make(InitializeWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        await workflow_service.execute(
            initialize_workflow,
            {
                "user_request": f"We are initializing the project and need the constition created.\n{raw_args}",
                "plan": initialize_workflow.get_plan(),
            },
        )

        self.emit_tui(Messages.CommandExecutionCompleted())
