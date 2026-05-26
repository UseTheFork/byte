from byte.constitution import (
    AddGovernanceRuleTool,
    AddPrincipleTool,
    AddSectionItemTool,
    AddSectionTool,
    ConstitutionAgentNode,
    ConstitutionWorkflow,
    DeleteGovernanceRuleTool,
    DeletePrincipleTool,
    DeleteSectionItemTool,
    DeleteSectionTool,
    UpdateMetaTool,
)
from byte.files import ListFilesTool
from byte.git import GitGrepTool
from byte.knowledge import AddFilesToContextTool
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import GraphBuilder, PhaseModel, RoutePhaseModel, UpdatePhaseTool
from byte.support import MD
from byte.system import UserConfirmOrInputTool, UserConfirmTool, UserInputTextTool, UserSelectTool


class InitializeWorkflow(ConstitutionWorkflow):
    """ """

    def get_phases(self, **kwargs):
        return [
            PhaseModel(
                id="consider-and-interview",
                content="Gather requirements and context for initializing the constitution.",
                note=[
                    MD.bullet("Interview the user about project values, principles, and governance needs."),
                    MD.bullet("The project may be brand new with no existing constitution file or documentation."),
                    MD.bullet("Infer context from any available repo files (README, docs, existing standards)."),
                    MD.bullet(
                        "The user might require less or more principles than the template provides. Respect their specification."
                    ),
                    MD.bullet("Clarify scope: which domains/areas does the constitution cover?"),
                ],
                tools=[
                    GitGrepTool,
                    ListFilesTool,
                    AddFilesToContextTool,
                    UserInputTextTool,
                    UserConfirmOrInputTool,
                    UserConfirmTool,
                    UserSelectTool,
                ],
                executed_by=ConstitutionAgentNode,
            ),
            PhaseModel(
                id="collect-derive",
                content="Collect/derive values for placeholders:",
                note=[
                    MD.bullet("If user input (conversation) supplies a value, use it."),
                    MD.bullet(
                        "Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded)."
                    ),
                    MD.bullet(
                        "For governance dates: `RATIFICATION_DATE` is the original adoption date, `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous."
                    ),
                    MD.bullet("`CONSTITUTION_VERSION` must increment according to semantic versioning rules:"),
                    MD.bullet("MAJOR: Backward incompatible governance/principle removals or redefinitions.", 2),
                    MD.bullet("MINOR: New principle/section added or materially expanded guidance.", 2),
                    MD.bullet("PATCH: Clarifications, wording, typo fixes, non-semantic refinements.", 2),
                    MD.bullet("If version bump type ambiguous, propose reasoning before finalizing."),
                ],
                tools=[
                    GitGrepTool,
                    UserSelectTool,
                    ListFilesTool,
                    AddFilesToContextTool,
                ],
                executed_by=ConstitutionAgentNode,
            ),
            PhaseModel(
                id="create",
                content="Write the draft constitution using the provided tools.",
                note=[
                    MD.bullet(
                        "The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly."
                    ),
                    MD.bullet(
                        "Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet - explicitly justify any left)."
                    ),
                    MD.bullet(
                        "Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance."
                    ),
                    MD.bullet(
                        "Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non-negotiable rules, explicit rationale if not obvious."
                    ),
                    MD.bullet(
                        "Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations."
                    ),
                ],
                executed_by=ConstitutionAgentNode,
                tools=[
                    AddGovernanceRuleTool,
                    AddSectionTool,
                    AddPrincipleTool,
                    AddSectionItemTool,
                    DeleteGovernanceRuleTool,
                    DeletePrincipleTool,
                    DeleteSectionItemTool,
                    DeleteSectionTool,
                    UpdateMetaTool,
                    UpdatePhaseTool,
                ],
            ),
            PhaseModel(
                id="validate-and-finalize",
                content="Validation final output:",
                note=[
                    MD.bullet("No remaining unexplained bracket tokens."),
                    MD.bullet("Version line matches report."),
                    MD.bullet(
                        'Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).'
                    ),
                ],
                tools=[
                    AddGovernanceRuleTool,
                    AddSectionTool,
                    AddPrincipleTool,
                    AddSectionItemTool,
                    DeleteGovernanceRuleTool,
                    DeletePrincipleTool,
                    DeleteSectionItemTool,
                    DeleteSectionTool,
                    UpdateMetaTool,
                    UpdatePhaseTool,
                ],
                executed_by=ConstitutionAgentNode,
            ),
            RoutePhaseModel(
                id="end",
                executed_by=EndNode,
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
