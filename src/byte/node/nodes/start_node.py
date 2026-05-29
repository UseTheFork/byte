from typing import Literal, Type

from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.node import BaseNode
from byte.orchestration import BaseState, MetadataSchema
from byte.orchestration.state import HarnessFiles, HarnessState
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
                files=HarnessFiles(
                    edit=state.get("harness", {}).get("files", {}).get("edit"),
                    create=state.get("harness", {}).get("files", {}).get("create"),
                    test=state.get("harness", {}).get("files", {}).get("test"),
                    reference=state.get("harness", {}).get("files", {}).get("reference"),
                ),
                reference_context=state.get("harness", {}).get("reference_context") or [],
                skills=state.get("harness", {}).get("skills") or [],
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
