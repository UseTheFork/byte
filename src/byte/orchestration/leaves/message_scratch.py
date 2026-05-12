from typing import TYPE_CHECKING, List

from langchain_core.messages import BaseMessage

from byte.orchestration import Leaf

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class MessageScratch(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> List[BaseMessage]:

        # TODO: Iterate over scratch messages and tag the last tool call with cache control.
        # "cache_control": {"type": "ephemeral"},
        return prompt_assembler.generate_scratch_state()
