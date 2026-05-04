from typing import TYPE_CHECKING

from byte.git import GitService
from byte.orchestration import Leaf
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class CommitHistory(Leaf):
    def __init__(self, as_section: bool = True):
        self.as_section = as_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        git_service = prompt_assembler.get_app().make(GitService)
        recent_commits = await git_service.get_recent_commits()

        if not recent_commits:
            return ""

        lines = []

        if self.as_section:
            lines.append(Section.start(SectionType.COMMIT_HISTORY))

        lines.append("Recent commits (newest first):")
        lines.append("")

        for c in recent_commits:
            files = ", ".join(c["files"]) if c["files"] else "none"
            lines.append(f"- [{c['short_hash']}] {c['message']}")
            lines.append(f"  author: {c['author']} | date: {c['date']}")
            lines.append(f"  files: {files}")

        if self.as_section:
            lines.append(Section.end())

        return list_to_multiline_text(lines)
