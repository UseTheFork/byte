import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.constitution import ConstitutionWorkflow
from byte.orchestration import WorkflowService
from byte.tui import Messages


class ConstitutionCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "constitution"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Ask the AI agent a question or request assistance",
        )
        parser.add_argument("constitution_query", nargs=argparse.REMAINDER, help="The user's question or query text")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """ """

        constitution_workflow = self.app.make(ConstitutionWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        await workflow_service.execute(
            constitution_workflow,
            {
                "user_request": raw_args,
                "workflow_phases": constitution_workflow.get_phases(),
            },
        )

        self.emit_tui(Messages.CommandExecutionCompleted())
