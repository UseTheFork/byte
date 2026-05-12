from byte.node.nodes import ToolNode
from byte.orchestration import GraphBuilder
from byte.skills import SkillCreatorAgentNode
from byte.workflow import BaseWorkflow


class CreateSkillWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=SkillCreatorAgentNode)

        # Add nodes
        graph.add_node(SkillCreatorAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
