from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState, MetadataSchema, Node
from byte.prompt_format import EditFormatService


class StartNode(Node):
    def boot(
        self,
        goto: str = "assistant_node",
        **kwargs,
    ):
        self.goto = goto

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["subprocess_node", "assistant_node"]]:
        edit_format = self.app.make(EditFormatService)

        result = {
            "agent": runtime.context.agent,
            "edit_format_system": edit_format.prompts.system,
            "masked_messages": [],
            "examples": edit_format.prompts.examples,
            "donts": [],
            "errors": None,
            "metadata": MetadataSchema(iteration=0),
        }

        return Command(
            goto=str(self.goto),
            update=result,
        )
