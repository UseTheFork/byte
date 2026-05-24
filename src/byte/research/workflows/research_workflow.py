from byte.files import AddFilesTool, ListFilesTool
from byte.git import GitGrepTool
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import (
    BaseWorkflow,
    CompleteTurnTool,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
)
from byte.research import ResearchAgentNode
from byte.system import UserSelectTool
from byte.web import SearchWebTool


class ResearchWorkflow(BaseWorkflow):
    """
    Primary workflow for AI-driven research and information gathering.

    Orchestrates a multi-phase graph pipeline that conducts research (phase 1)
    and summarizes findings (phase 2), terminating at an end node (phase 3).
    """

    def get_phases(self, **kwargs):
        return [
            PhaseModel(
                id="research",
                content="Conduct research to gather information and answer the user's question. Use available tools to search the web, grep through code, list and add files as needed.",
                executed_by=ResearchAgentNode,
                tools=[
                    SearchWebTool,
                    GitGrepTool,
                    UserSelectTool,
                    ListFilesTool,
                    AddFilesTool,
                ],
                tool_choice="any",
            ),
            PhaseModel(
                id="summary",
                content="Compile and summarize all research findings and present them to the user.",
                executed_by=ResearchAgentNode,
                tools=[
                    CompleteTurnTool,
                ],
            ),
            RoutePhaseModel(
                id="end",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        graph = self.app.make(GraphBuilder, start_node=ResearchAgentNode)

        # Add nodes
        graph.add_node(ResearchAgentNode)
        graph.add_node(ToolNode)
        graph.add_node(EndNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
