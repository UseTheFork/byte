from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from langchain_core.messages import BaseMessage

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class MessageFragment(ABC):
    @abstractmethod
    async def assemble(self, prompt_assembler: PromptAssembler) -> BaseMessage | List[BaseMessage]: ...
