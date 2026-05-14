from typing import TYPE_CHECKING, override

from langchain_core.messages import SystemMessage

from byte.orchestration import MessageFragment

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class System(MessageFragment):
    @override
    async def assemble(self, prompt_assembler: PromptAssembler) -> SystemMessage:

        system_message = prompt_assembler.get_assembled_state().get("system_message")

        return SystemMessage(
            content=[
                {
                    "type": "text",
                    "text": system_message,
                    "cache_control": {"type": "ephemeral"},
                },
            ]
        )
