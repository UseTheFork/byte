from argparse import Namespace
from typing import List

from byte import ByteArgumentParser, Command
from byte.coder import CoderWorkflow
from byte.orchestration import PhaseUtils, WorkflowService
from byte.specs import SpecLoaderService
from byte.tui import Messages


class SpecExecuteCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "spec"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Execute or continue executing a spec",
        )
        parser.add_argument("spec", help="The task id")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:

        coder_workflow = self.app.make(CoderWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        workflow_phases = PhaseUtils.to_phase_dict(coder_workflow.get_phases())

        # Specs are executed via the coder workflow one by one and are just passed in via a user request and a files context.
        spec_loader_service = self.app.make(SpecLoaderService)
        tasks = spec_loader_service.load_tasks(args.spec)

        for task in tasks:
            task.to_md()
            await workflow_service.execute(
                coder_workflow,
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
