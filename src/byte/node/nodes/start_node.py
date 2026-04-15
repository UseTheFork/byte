from typing import Literal, Type

from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.node import BaseNode
from byte.orchestration import AssistantContextSchema, BaseState, MetadataSchema, PromptSettingsSchema
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
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:
        prompt_settings = (
            runtime.context.prompt_settings if hasattr(runtime.context, "prompt_settings") else PromptSettingsSchema()
        )

        result = {
            # We always remove scratch no matter what.
            "scratch_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
            "masked_messages": [],
            "parsed_blocks": [],
            "extracted_content": None,
            "errors": None,
            "metadata": MetadataSchema(
                iteration=0,
                erase_history=False,
                prompt_settings=prompt_settings,
            ),
        }

        return self.route_to(
            self.goto,
            result,
        )
