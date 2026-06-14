import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.documentation import DocumentationWorkflow
from byte.orchestration import PhaseUtils, WorkflowService
from byte.tui import Messages


class DocumentationCommand(Command):
    """Execute documentation operations from the CLI."""

    @property
    def name(self) -> str:
        return "docs"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Ask the AI agent to perform a documentation operation",
        )
        parser.add_argument("documentation_request", nargs=argparse.REMAINDER, help="The user's request")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the documentation workflow with the provided user request."""

        documentation_workflow = self.app.make(DocumentationWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        workflow_phases = PhaseUtils.to_phase_dict(documentation_workflow.get_phases())
        await workflow_service.execute(
            documentation_workflow, {"user_request": raw_args, "workflow_phases": workflow_phases}
        )

        self.emit_tui(Messages.CommandExecutionCompleted())
