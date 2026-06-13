from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.constitution import (
    Constitution,
    ConstitutionGovernanceRule,
    ConstitutionItem,
    ConstitutionMeta,
    ConstitutionPrinciple,
    ConstitutionSection,
    ConstitutionService,
    InitializeWorkflow,
)
from byte.orchestration import PhaseUtils, WorkflowService
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
        user_request_lines = []

        interaction_service = self.app.make(InteractionService)
        today = __import__("datetime").date.today().isoformat()

        principles = {}

        include = await interaction_service.confirm("Enable DDD (Domain Driven Design)?", default=True)
        if include:
            ddd = ConstitutionPrinciple(
                id="ddd",
                order=10,
                name="Domain Driven Design",
                description="All business logic MUST be organized into bounded-context domains under [DOMAIN_LOCATION]. Cross-domain communication MUST occur through explicit public interfaces — never by reaching into another domain's internals. New features MUST be placed in the appropriate existing domain or justify the creation of a new one.",
            )
            user_request_lines.append("I want the project to follow Domain Driven Design (DDD).")
            principles[ddd.id] = ddd

        include = await interaction_service.confirm("Enable DRY (Don't Repeat Yourself)?", default=True)
        if include:
            dry = ConstitutionPrinciple(
                id="dry",
                order=20,
                name="Don't Repeat Yourself (DRY)",
                description="All code MUST avoid unnecessary duplication of logic, configuration, and data definitions. Shared behavior MUST be extracted into reusable services, utilities, or base classes and resolved through the application container or established import patterns. When identical or near-identical logic exists in more than one location, it MUST be consolidated into a single authoritative source. Duplication in test fixtures, schema definitions, and prompt templates MUST be reduced through shared factories, constants, or helper modules. Shared logic MUST be extracted into [SHARED_LOGIC_LOCATION]",
            )
            user_request_lines.append("I want the project to follow Don't Repeat Yourself (DRY).")
            principles[dry.id] = dry

        include = await interaction_service.confirm("Enable TDD (Test Driven Development)?", default=True)
        if include:
            tdd = ConstitutionPrinciple(
                id="tdd",
                order=30,
                name="TDD (Test Driven Development)",
                description="All new functionality MUST be accompanied by tests written before or alongside the implementation. The test suite MUST pass before any code is considered complete. [TESTING_LOCATION]. [TESTING_FRAMEWORK] is the required testing framework.",
            )
            user_request_lines.append("I want the project to follow TDD (Test Driven Development).")
            principles[tdd.id] = tdd

        include = await interaction_service.confirm("Enable YAGNI (You Aren't Gonna Need It)?", default=True)
        if include:
            yagni = ConstitutionPrinciple(
                id="yagni",
                order=40,
                name="You Aren't Gonna Need It (YAGNI)",
                description="Code MUST only be written to satisfy current, concrete requirements — never on speculation of future needs. Abstractions, configuration options, and extension points MUST NOT be introduced until a real use case demands them. Remove dead code promptly.",
            )
            user_request_lines.append("I want the project to follow You Aren't Gonna Need It (YAGNI).")
            principles[yagni.id] = yagni

        include = await interaction_service.confirm("Enable TDA (Tell, Don't Ask)?", default=True)
        if include:
            tda = ConstitutionPrinciple(
                id="tda",
                order=50,
                name="TDA (Tell, Don't Ask)",
                description="Objects MUST expose behavior through commands that perform work internally rather than exposing state for external decision-making. Callers MUST tell objects what to do - not query their state and act on the result. Logic that depends on an object's internal state MUST reside within that object. Getter-heavy interfaces MUST be refactored to move the dependent logic into the owning class or module.",
            )
            user_request_lines.append("I want the project to follow Tell, Don't Ask (TDA).")
            principles[tda.id] = tda

        include = await interaction_service.confirm("Enable Strict Typing?", default=True)
        if include:
            strict_typing = ConstitutionPrinciple(
                id="strict-typing",
                order=60,
                name="Strict Typing",
                description="All function signatures MUST include explicit type annotations for parameters and return types. All variables MUST have type annotations where types are not obvious from context. Use of `Any` is prohibited unless explicitly justified with a comment. Type-checking tools MUST pass cleanly with no errors or unresolved type issues.",
            )
            user_request_lines.append("I want the project to follow Strict Typing.")
            principles[strict_typing.id] = strict_typing

        sections = {}

        include = await interaction_service.confirm("Include Tooling & Framework Standards section?", default=True)
        if include:
            frameworks = await interaction_service.input_text(
                "What frameworks will this project use? (e.g., Laravel, Django, FastAPI)"
            )
            if frameworks.value.strip():
                user_request_lines.append("What frameworks will this project use?")
                user_request_lines.append(frameworks.value.strip())

            linting_tools = await interaction_service.input_text(
                "What linting and formatting tools will this project use? (e.g., RUFF, prettier, pint)"
            )
            if linting_tools.value.strip():
                user_request_lines.append("What linting and formatting tools will this project use?")
                user_request_lines.append(linting_tools.value.strip())

            framework_item = ConstitutionItem(
                id="framework-standards",
                section_id="tooling-framework-standards",
                name="Framework Standards",
                content="Define the approved frameworks and their usage patterns for this project. [FRAMEWORK_LOCATION]",
                order=10,
            )

            linting_item = ConstitutionItem(
                id="linting-formatting",
                section_id="tooling-framework-standards",
                name="Linting and Formatting Standards",
                content="Define the linting and formatting tools, configurations, and expectations for code quality. [LINTING_TOOLS_LOCATION]",
                order=20,
            )

            tooling_section = ConstitutionSection(
                id="tooling-framework-standards",
                name="Tooling & Framework Standards",
                applies_to=["*"],
                items={
                    framework_item.id: framework_item,
                    linting_item.id: linting_item,
                },
                order=10,
            )
            sections[tooling_section.id] = tooling_section

        confirmed, text_input = await interaction_service.confirm_or_input(
            "Ready to Role?", "Enter your additional comments:", default_confirm=False
        )
        if confirmed and text_input:
            user_request_lines.append("")
            user_request_lines.append("Additional Comments:")
            user_request_lines.append(text_input.value.strip())

        combined_lines = (
            "We are initializing the project and need the constition created. Here are the answers to a generic questioner the user completed:"
            + list_to_multiline_text(user_request_lines)
        )

        supremacy = ConstitutionGovernanceRule(
            id="supremacy",
            order=990,
            name="Supremacy",
            content="This constitution supersedes all other project practices, conventions, and ad-hoc agreements. Amendments require documentation and explicit approval. All contributors — human and automated — MUST comply.",
        )
        versioning_policy = ConstitutionGovernanceRule(
            id="versioning-policy",
            order=999,
            name="Versioning Policy",
            content="Constitution versions follow semantic versioning: MAJOR for principle removals or backward-incompatible redefinitions, MINOR for new principles or materially expanded guidance, PATCH for wording clarifications and non-semantic refinements.",
        )

        constitution = Constitution(
            principles=principles,
            governance={
                supremacy.id: supremacy,
                versioning_policy.id: versioning_policy,
            },
            sections=sections,
            meta=ConstitutionMeta(version="0.1.0", ratified=today, last_amended=today),
        )

        constitution_service = self.app.make(ConstitutionService)
        constitution_service.save_and_set_current(constitution)

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
