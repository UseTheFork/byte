from byte.constitution import (
    AddGovernanceRuleTool,
    AddPrincipleTool,
    AddSectionItemTool,
    ConstitutionAgentNode,
    DeleteGovernanceRuleTool,
    DeletePrincipleTool,
    DeleteSectionItemTool,
    DeleteSectionTool,
    UpdateMetaTool,
)
from byte.files import AddFilesTool, ListFilesTool
from byte.git import GitGrepTool
from byte.node.nodes import ToolNode
from byte.orchestration import BaseWorkflow, GraphBuilder, PhaseModel
from byte.plan import ConfirmCompletePlanStepTool
from byte.support.section import Section, SectionType
from byte.system import UserSelectTool


class ConstitutionWorkflow(BaseWorkflow):
    """ """

    def get_phases(self):
        return [
            PhaseModel(
                id="1",
                content=f"Consider the existing constitution at {Section.ref(SectionType.CONSTITUTION)}",
                note=[
                    Section.important(
                        "The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly."
                    ),
                ],
                agent=ConstitutionAgentNode,
            ),
            PhaseModel(
                id="2",
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
                agent=ConstitutionAgentNode,
            ),
            PhaseModel(
                id="3",
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
                agent=ConstitutionAgentNode,
                completion_mode="confirm",
            ),
            PhaseModel(
                id="4",
                content="Validation before final output:",
                note=[
                    "   - No remaining unexplained bracket tokens.",
                    "   - Version line matches report.",
                    '   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).',
                ],
                agent=ConstitutionAgentNode,
            ),
            PhaseModel(
                id="5",
                content="Write the completed constitution using the provided tools.",
                agent=ConstitutionAgentNode,
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

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=ConstitutionAgentNode)

        # Add nodes
        graph.add_node(ConstitutionAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
