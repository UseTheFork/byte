from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import (
    BaseWorkflow,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
    UpdatePhaseTool,
)
from byte.skills import SkillSelectAgentNode
from byte.specs import CreateTaskTool, SpecTaskCreatorAgentNode


class CreateSpecPhaseWorkflow(BaseWorkflow):
    """ """

    def get_phases(self, **kwargs):
        return [
            PhaseModel(
                id="select-skills",
                content="Identify and load the relevant skills based on the user's task",
                executed_by=SkillSelectAgentNode,
                note=[
                    f"If no skills are relvent complete this phase using the `{UpdatePhaseTool.name}` tool.",
                ],
                tools=[
                    UpdatePhaseTool,
                ],
                tool_choice="any",
            ),
            PhaseModel(
                id="create-phases",
                content="Create the phases - use available tools to create the phases.",
                tools=[
                    CreateTaskTool,
                ],
                executed_by=SpecTaskCreatorAgentNode,
            ),
            RoutePhaseModel(
                id="end",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=SpecTaskCreatorAgentNode)

        # Add nodes
        graph.add_node(SpecTaskCreatorAgentNode)
        graph.add_node(SkillSelectAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
