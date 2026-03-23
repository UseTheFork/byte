from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState
from byte.agent.nodes.model.base_model_node import BaseModelNode
from byte.llm import LLMService


class MainModelNode(BaseModelNode):
    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:
        # record_response_service = self.app.make(RecordResponseService)

        agent_state, config = await self._generate_agent_state(state, config, runtime.context)

        # Select model based on mode
        llm_service = self.app.make(LLMService)
        runnable = self._create_runnable(llm_service.get_main_model(), runtime.context)

        result = await runnable.ainvoke(agent_state, config=config)
        # await record_response_service.record_response(agent_state, runnable, runtime, config)

        if result.tool_calls and len(result.tool_calls) > 0:
            return Command(
                goto="routing_node",
                update={"scratch_messages": [result], "errors": None, "node_to": "tool_node"},
            )

        return Command(
            goto="routing_node",
            update={"scratch_messages": [result], "errors": None, "node_to": str(self.goto)},
        )
