from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class Leaf(ABC):
    @abstractmethod
    async def assemble(self, prompt_assembler: PromptAssembler) -> str: ...
