from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.llm import LLMService
from byte.node import ModelBaseNode
from byte.orchestration import AssistantContextSchema, BaseState


class ModelWeakNode(ModelBaseNode):
    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["end_node", "parse_blocks_node", "tool_node", "validation_node"]]:
        # record_response_service = self.app.make(RecordResponseService)

        agent_state, config = await self._generate_agent_state(state, config, runtime.context)

        # Select model based on mode
        llm_service = self.app.make(LLMService)
        runnable = self._create_runnable(llm_service.get_weak_model(), runtime.context)

        result = await runnable.ainvoke(agent_state, config=config)

        if result.tool_calls and len(result.tool_calls) > 0:
            return Command(
                goto="tool_node",
                update={
                    "scratch_messages": [result],
                    "errors": None,
                },
            )

        return Command(
            goto=str(self.goto),
            update={
                "scratch_messages": [result],
                "errors": None,
            },
        )
