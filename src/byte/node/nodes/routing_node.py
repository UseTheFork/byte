from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.node import BaseNode
from byte.orchestration import BaseState, PhaseUtils, WorkflowService


# This is here to control the below Literal and be able to have all possible nodes in one place.
class RoutingNode(BaseNode):
    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[
        Literal[
            "end_node",
            "tool_node",
            "commit_agent_node",
            "constitution_agent_node",
            "coder_agent_node",
            "skill_creator_agent_node",
            "skill_select_agent_node",
            "ask_agent_node",
        ]
    ]:
        routing = state.get("routing", {})

        # Check if the user has cancelled execution
        workflow_service = self.app.make(WorkflowService)
        if workflow_service.cancel_event.is_set():
            return Command(goto="end_node")

        # Check where we are in the workflow
        if PhaseUtils.is_workflow_agent(state) and routing.get("target") not in ("tool_node", "end_node"):
            pending_phase = PhaseUtils.get_pending_phase(state)
            if pending_phase:
                self.app["log"].info(f"Routing Phase >> To: {pending_phase.get_executed_by()}")
                return Command(goto=pending_phase.get_executed_by())  # ty:ignore[invalid-return-type]

        self.app["log"].info(f"Routing >> From: {routing.get('source')} >> To: {routing.get('target')}")
        return Command(goto=routing.get("target"))  # ty:ignore[invalid-return-type]
