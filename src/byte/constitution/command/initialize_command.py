import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.tui import Messages
from byte.workflow import ConstitutionWorkflow, WorkflowService


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
            description="Ask the AI agent a question or request assistance",
        )
        parser.add_argument("ask_query", nargs=argparse.REMAINDER, help="The user's question or query text")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """ """

        ask_workflow = self.app.make(ConstitutionWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        await workflow_service.execute(
            ask_workflow,
            {"user_request": f"We are initializing the project and need the constition created.\n{raw_args}"},
        )

        self.emit_tui(Messages.CommandExecutionCompleted())
