import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.constitution import (
    AddGovernanceRuleTool,
    AddPrincipleTool,
    AddSectionItemTool,
    ConstitutionAgentNode,
    ConstitutionWorkflow,
    DeleteGovernanceRuleTool,
    DeletePrincipleTool,
    DeleteSectionItemTool,
    DeleteSectionTool,
    UpdateMetaTool,
)
from byte.files import AddFilesTool, ListFilesTool
from byte.git import GitGrepTool
from byte.plan import ConfirmCompletePlanStepTool
from byte.plan.models import PlanStep
from byte.support.section import Section, SectionType
from byte.system import UserSelectTool
from byte.tui import Messages
from byte.workflow import WorkflowService


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
        """ """

        ask_workflow = self.app.make(ConstitutionWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        plan = [
            PlanStep(
                id="1",
                order=1,
                content=f"Consider the existing constitution at {Section.ref(SectionType.CONSTITUTION)}",
                note=[
                    Section.important(
                        "The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly."
                    ),
                ],
                agent=ConstitutionAgentNode.name,
            ),
            PlanStep(
                id="2",
                order=2,
                content="Collect/derive values for placeholders:",
                note=[
                    "   - If user input (conversation) supplies a value, use it.",
                    "   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).",
                    "   - For governance dates: `RATIFICATION_DATE` is the original adoption date, `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.",
                    "   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:",
                    "     - MAJOR: Backward incompatible governance/principle removals or redefinitions.",
                    "     - MINOR: New principle/section added or materially expanded guidance.",
                    "     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.",
                    "   - If version bump type ambiguous, propose reasoning before finalizing.",
                ],
                tools=[
                    GitGrepTool,
                    UserSelectTool,
                    ListFilesTool,
                    AddFilesTool,
                ],
                agent=ConstitutionAgentNode.name,
            ),
            PlanStep(
                id="3",
                order=3,
                content="Draft the updated constitution content:",
                note=[
                    "   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet - explicitly justify any left).",
                    "   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.",
                    "   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non-negotiable rules, explicit rationale if not obvious.",
                    "   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.",
                    f"  - Use the `{ConfirmCompletePlanStepTool.name}` tool to confirm and get access to the tools needed to make the final edits.",
                ],
                tools=[
                    GitGrepTool,
                    UserSelectTool,
                    ListFilesTool,
                    AddFilesTool,
                ],
                agent=ConstitutionAgentNode.name,
                completion_mode="confirm",
            ),
            PlanStep(
                id="4",
                order=4,
                content="Validation before final output:",
                note=[
                    "   - No remaining unexplained bracket tokens.",
                    "   - Version line matches report.",
                    '   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).',
                ],
                agent=ConstitutionAgentNode.name,
            ),
            PlanStep(
                id="5",
                order=5,
                content="Write the completed constitution using the provided tools.",
                agent=ConstitutionAgentNode.name,
                tools=[
                    AddGovernanceRuleTool,
                    AddPrincipleTool,
                    AddSectionItemTool,
                    DeleteGovernanceRuleTool,
                    DeletePrincipleTool,
                    DeleteSectionItemTool,
                    DeleteSectionTool,
                    UpdateMetaTool,
                ],
            ),
        ]

        workflow_service = self.app.make(WorkflowService)
        await workflow_service.execute(
            ask_workflow,
            {
                "user_request": f"We are initializing the project and need the constition created.\n{raw_args}",
                "plan": plan,
            },
        )

        self.emit_tui(Messages.CommandExecutionCompleted())
