from byte.coder import CoderAgentNode
from byte.files import (
    DeleteFileTool,
    EditFileTool,
    ReplaceFileTool,
    WriteFileTool,
)
from byte.node.nodes import LintNode, ToolNode
from byte.orchestration import GraphBuilder
from byte.plan import CompletePlanStepTool, CreatePlanTool, PlanStep
from byte.workflow import BaseWorkflow


class CoderWorkflow(BaseWorkflow):
    """ """

    def get_plan(self):
        return [
            PlanStep(
                id="1",
                order=1,
                content="Create a clear, step-by-step plan for implementing the requested changes.",
                note=[
                    f"When possible use the `{CreatePlanTool.name}` tool in parallel with the `{CompletePlanStepTool.name}` tool"
                ],
                agent=CoderAgentNode,
                tools=[
                    CreatePlanTool,
                ],
            ),
            PlanStep(
                id="2",
                order=2,
                content="Use available tools to apply the changes to complete the step-by-step plan",
                tools=[
                    EditFileTool,
                    WriteFileTool,
                    DeleteFileTool,
                    ReplaceFileTool,
                ],
                agent=CoderAgentNode,
            ),
        ]

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=CoderAgentNode)

        # Add nodes
        graph.add_node(CoderAgentNode, goto=LintNode)
        graph.add_node(ToolNode)
        graph.add_node(LintNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
