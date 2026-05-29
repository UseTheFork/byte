from byte.harness import BootstrapSkillsTool, HarnessAgentNode
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import (
    BaseWorkflow,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
)
from byte.specs import CreateTaskTool, SpecTaskCreatorAgentNode


class CreateSpecTaskWorkflow(BaseWorkflow):
    """ """

    def get_phases(self, **kwargs):
        return [
            PhaseModel(
                id="select-skills",
                content="Identify and load the relevant skills based on the user's task",
                executed_by=HarnessAgentNode,
                tools=[
                    BootstrapSkillsTool,
                ],
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

        graph = self.app.make(GraphBuilder, start_node=HarnessAgentNode)

        # Add nodes
        graph.add_node(SpecTaskCreatorAgentNode)
        graph.add_node(HarnessAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
