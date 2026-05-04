from typing import TYPE_CHECKING

from byte.git import CommitService
from byte.orchestration import Leaf

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class CommitGuidelines(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        commit_service = prompt_assembler.get_app().make(CommitService)
        git_guidelines = await commit_service.generate_commit_guidelines()
        return git_guidelines
