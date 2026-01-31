from typing import Type

from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, AssistantNode, BaseState, MetadataSchema, Node
from byte.prompt_format import EditFormatService
from byte.support import Str


class StartNode(Node):
    def boot(
        self,
        goto: Type[Node] = AssistantNode,
        **kwargs,
    ):
        self.goto = Str.class_to_snake_case(goto)

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[str]:
        edit_format = self.app.make(EditFormatService)

        result = {
            "agent": runtime.context.agent,
            "edit_format_system": edit_format.prompts.system,
            # We always remove scratch no matter what.
            "scratch_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
            "masked_messages": [],
            "examples": edit_format.prompts.examples,
            "parsed_blocks": [],
            "extracted_content": None,
            "errors": None,
            "metadata": MetadataSchema(
                iteration=0,
                erase_history=False,
            ),
        }

        return Command(
            goto=str(self.goto),
            update=result,
        )
