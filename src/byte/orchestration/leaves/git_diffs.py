from typing import TYPE_CHECKING

from byte.git import CommitService
from byte.orchestration import Leaf
from byte.support import Section
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class GitDiffs(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:

        commit_service = prompt_assembler.get_app().make(CommitService)
        git_diffs = await commit_service.build_commit_prompt()

        lines = [
            Section.sub_heading("Git Diffs", 2),
            "```",
            git_diffs.get("git_diffs", ""),
            "```",
            Section.important("You **MUST** consider the above git diffs before proceeding (if not empty)."),
            Section.end(),
        ]

        return list_to_multiline_text(lines)
