import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.coder import CoderAgentNode, CoderWorkflow
from byte.files import (
    DeleteFileTool,
    EditFileTool,
    ReplaceFileTool,
    WriteFileTool,
)
from byte.plan import CreatePlanTool, PlanStep
from byte.tui import Messages
from byte.workflow import WorkflowService


# TODO: need to add docs
class CoderCommand(Command):
    """C"""

    @property
    def name(self) -> str:
        return "coder"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Ask the AI agent to perform a code operation",
        )
        parser.add_argument("coder_request", nargs=argparse.REMAINDER, help="The user's request")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """ """

        plan = [
            PlanStep(
                id="1",
                order=1,
                content="Create a clear, step-by-step plan for implementing the requested changes.",
                agent=CoderAgentNode,
                tools=[
                    CreatePlanTool,
                ],
            ),
            PlanStep(
                id="2",
                order=2,
                content="Use available tools to apply the changes.",
                tools=[
                    EditFileTool,
                    WriteFileTool,
                    DeleteFileTool,
                    ReplaceFileTool,
                ],
                agent=CoderAgentNode,
            ),
        ]

        ask_workflow = self.app.make(CoderWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        await workflow_service.execute(ask_workflow, {"user_request": raw_args, "plan": plan})

        self.emit_tui(Messages.CommandExecutionCompleted())
