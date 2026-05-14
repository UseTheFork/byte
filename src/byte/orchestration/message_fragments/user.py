from typing import TYPE_CHECKING, override

from langchain.messages import HumanMessage

from byte.orchestration import MessageFragment

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class User(MessageFragment):
    @override
    async def assemble(self, prompt_assembler: PromptAssembler) -> HumanMessage:

        user_message = prompt_assembler.get_assembled_state().get("user_message")

        return HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": user_message,
                    "cache_control": {"type": "ephemeral"},
                },
            ]
        )
