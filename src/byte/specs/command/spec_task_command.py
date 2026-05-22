import argparse
from argparse import Namespace
from typing import List

from byte import ByteArgumentParser, Command
from byte.orchestration import PhaseUtils, WorkflowService
from byte.specs import CreateSpecPhaseWorkflow, SpecLoaderService
from byte.tui import Messages


class SpecTaskCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "spec-task"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Have an agent create a new task",
        )
        parser.add_argument("task", help="The task id")
        parser.add_argument("task_query", nargs=argparse.REMAINDER, help="The user's query to generate the task for")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:

        create_spec_phase_workflow = self.app.make(CreateSpecPhaseWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        workflow_phases = PhaseUtils.to_phase_dict(create_spec_phase_workflow.get_phases())

        await workflow_service.execute(
            create_spec_phase_workflow,
            {
                "user_request": " ".join(args.task_query),
                "harness": {"spec": args.task},
                "workflow_phases": workflow_phases,
            },
        )

        self.emit_tui(Messages.CommandExecutionCompleted())

    async def get_completions(self, text: str) -> List[str]:
        """Provide intelligent spec name completions from loaded specs."""
        try:
            spec_loader_service = self.app.make(SpecLoaderService)

            # Get all spec names and filter by pattern match
            spec_names = list(spec_loader_service.specs.keys())
            return [name for name in spec_names if name.startswith(text.lower())]
        except Exception:
            # Fallback to empty list if discovery fails
            return []
