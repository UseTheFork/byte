import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.constitution import InitializeWorkflow
from byte.orchestration import PhaseUtils, WorkflowService
from byte.support import MD
from byte.support.utils import list_to_multiline_text
from byte.tui import InteractionService, Messages


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
        lines = []

        interaction_service = self.app.make(InteractionService)

        principles = [
            ("DDD (Domain Driven Design)", "DDD"),
            ("DRY (Don't Repeat Yourself)", "DRY"),
            ("TDD (Test Driven Development)", "TDD"),
            ("YAGNI (You Aren't Gonna Need It)", "YAGNI"),
        ]

        for principle_name, _ in principles:
            include = await interaction_service.confirm(f"Include {principle_name}?", default=True)
            lines.append(MD.bullet("Include a principle / sections on:"))
            if include:
                lines.append(MD.bullet(principle_name))

        frameworks = await interaction_service.input_text(
            "What frameworks will this project use? (e.g., Laravel, Django, FastAPI)"
        )
        if frameworks.value.strip():
            lines.append(MD.bullet(f"Project frameworks: {frameworks}"))

        testing_frameworks = await interaction_service.input_text(
            "What testing frameworks will this project use? (e.g., PEST, pytest, Vitest)"
        )
        if testing_frameworks.value.strip():
            lines.append(MD.bullet(f"Testing frameworks: {testing_frameworks}"))

        linting_tools = await interaction_service.input_text(
            "What linting and formatting tools will this project use? (e.g., RUFF, prettier, pint)"
        )
        if linting_tools.value.strip():
            lines.append(MD.bullet(f"Linting and formatting tools: {linting_tools}"))

        if args.constitution_query:
            query_text = " ".join(args.constitution_query)
            lines.append("")
            lines.append("Additional context:")
            lines.append(query_text)

        combined_lines = list_to_multiline_text(lines)

        initialize_workflow = self.app.make(InitializeWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        workflow_phases = PhaseUtils.to_phase_dict(initialize_workflow.get_phases())

        await workflow_service.execute(
            initialize_workflow,
            {
                "user_request": f"We are initializing the project and need the constition created.\n{combined_lines}",
                "workflow_phases": workflow_phases,
            },
        )

        self.emit_tui(Messages.CommandExecutionCompleted())
