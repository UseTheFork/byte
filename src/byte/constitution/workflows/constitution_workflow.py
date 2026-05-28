from byte.constitution import (
    AddGovernanceRuleTool,
    AddPrincipleTool,
    AddSectionItemTool,
    AddSectionTool,
    ConstitutionAgentNode,
    DeleteGovernanceRuleTool,
    DeletePrincipleTool,
    DeleteSectionItemTool,
    DeleteSectionTool,
    UpdateMetaTool,
)
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import (
    BaseWorkflow,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
    UpdatePhaseTool,
)
from byte.support import MD, Section, SectionType
from byte.system import UserConfirmOrInputTool, UserConfirmTool, UserInputTextTool, UserSelectTool


class ConstitutionWorkflow(BaseWorkflow):
    """ """

    def get_phases(self, **kwargs):
        return [
            PhaseModel(
                id="consider",
                content=f"Consider the existing constitution at {Section.ref(SectionType.CONSTITUTION)}",
                note=[
                    MD.bullet(
                        "The user might require less or more principles / sections than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly."
                    ),
                    MD.bullet(f"You MUST use the {UpdatePhaseTool.name} to complete this phase."),
                ],
                tools=[
                    UserInputTextTool,
                    UserConfirmOrInputTool,
                    UserConfirmTool,
                    UserSelectTool,
                    UpdatePhaseTool,
                ],
                executed_by=ConstitutionAgentNode,
            ),
            PhaseModel(
                id="update",
                content="Make the changes to the constitution using the provided tools.",
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
