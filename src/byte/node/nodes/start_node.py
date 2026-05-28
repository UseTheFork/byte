from typing import Literal, Type

from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.node import BaseNode
from byte.orchestration import BaseState, MetadataSchema
from byte.orchestration.state import HarnessState
from byte.support import Str


class StartNode(BaseNode):
    def boot(
        self,
        goto: Type[BaseNode],
        **kwargs,
    ):
        self.goto = Str.class_to_snake_case(goto)

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        record_response_service = self.app.make(RecordResponseService)

        self.app.dispatch_task(
            record_response_service.clear_cache(config),
        )

        result = {
            # We always remove scratch no matter what.
            "scratch_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
            "touched_files": state.get("touched_files") or [],
            "workflow_phases": state.get("workflow_phases") or [],
            "errors": None,
            "harness": HarnessState(
                instruction=state.get("harness", {}).get("instruction") or "",
                spec=state.get("harness", {}).get("spec") or "",
                editable_files=state.get("harness", {}).get("editable_files") or [],
                reference_files=state.get("harness", {}).get("reference_files") or [],
                reference_context=state.get("harness", {}).get("reference_context") or [],
                skills=[],
            ),
            "metadata": MetadataSchema(
                iteration=0,
                erase_history=False,
            ),
            "is_cancelled": False,
        }

        return self.route_to(
            self.goto,
            result,
        )
