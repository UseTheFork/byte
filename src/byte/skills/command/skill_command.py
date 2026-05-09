import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.skills import CreateSkillWorkflow
from byte.tui import Messages
from byte.workflow import WorkflowService


class SkillCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "skill"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Have an agent create a new skill",
        )
        parser.add_argument("skill_query", nargs=argparse.REMAINDER, help="The user's query to geneate the skill for")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """ """

        ask_workflow = self.app.make(CreateSkillWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        await workflow_service.execute(ask_workflow, {"user_request": raw_args})

        self.emit_tui(Messages.CommandExecutionCompleted())
