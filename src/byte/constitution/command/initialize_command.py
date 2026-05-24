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

        lines.append(MD.bullet("Include a principle / sections on:"))
        for principle_name, _ in principles:
            include = await interaction_service.confirm(f"Include {principle_name}?", default=True)
            if include:
                lines.append(MD.bullet(f"Include a principle / sections on {principle_name}: Yes"))

        frameworks = await interaction_service.input_text(
            "What frameworks will this project use? (e.g., Laravel, Django, FastAPI)"
        )
        if frameworks.value.strip():
            lines.append(f"\n\nWhat frameworks will this project use?\n\n {frameworks.value.strip()}")

        testing_frameworks = await interaction_service.input_text(
            "What testing frameworks will this project use? (e.g., PEST, pytest, Vitest)"
        )
        if testing_frameworks.value.strip():
            lines.append(f"\n\nWhat testing frameworks will this project use?\n\n {testing_frameworks.value.strip()}")

        linting_tools = await interaction_service.input_text(
            "What linting and formatting tools will this project use? (e.g., RUFF, prettier, pint)"
        )
        if linting_tools.value.strip():
            lines.append(
                f"\n\nWhat linting and formatting tools will this project use? \n\n {linting_tools.value.strip()}"
            )

        confirmed, text_input = await interaction_service.confirm_or_input(
            "Do you have any other comments to add?", "Enter your additional comments:", default_confirm=False
        )
        if not confirmed and text_input:
            lines.append("")
            lines.append("Additional Comments:")
            lines.append(text_input.value.strip())

        combined_lines = (
            "We are initializing the project and need the constition created. Here are the answers to a generic questioner the user completed:"
            + list_to_multiline_text(lines)
        )

        initialize_workflow = self.app.make(InitializeWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(combined_lines, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        workflow_phases = PhaseUtils.to_phase_dict(initialize_workflow.get_phases())

        await workflow_service.execute(
            initialize_workflow,
            {
                "user_request": combined_lines,
                "workflow_phases": workflow_phases,
            },
        )

        self.emit_tui(Messages.CommandExecutionCompleted())
