from typing import TYPE_CHECKING, override

from langchain.messages import HumanMessage

from byte.orchestration import MessageFragment

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class Context(MessageFragment):
    @override
    async def assemble(self, prompt_assembler: PromptAssembler) -> HumanMessage:

        context_message = prompt_assembler.get_assembled_state().get("context_message")

        return HumanMessage(
            content=[
                {"type": "text", "text": context_message},
            ]
        )
