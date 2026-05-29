import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.orchestration import PhaseUtils, WorkflowService
from byte.specs import CreateRefractorWorkflow
from byte.tui import Messages


class RefractorCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "refractor"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Have an agent create a new refactoring spec",
        )
        parser.add_argument("refractor_query", nargs=argparse.REMAINDER, help="The user's query to generate the spec for")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:

        create_refractor_workflow = self.app.make(CreateRefractorWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        workflow_phases = PhaseUtils.to_phase_dict(create_refractor_workflow.get_phases())
        await workflow_service.execute(
            create_refractor_workflow, {"user_request": raw_args, "workflow_phases": workflow_phases}
        )

        self.emit_tui(Messages.CommandExecutionCompleted())
