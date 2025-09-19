from typing import TYPE_CHECKING

from byte.core.command.registry import Command
from byte.domain.agent.commit.service import CommitService

if TYPE_CHECKING:
    pass


class CommitCommand(Command):
    """Command to generate AI-powered git commit messages from staged changes.

    Analyzes staged git changes and uses LLM to generate conventional commit
    messages following best practices. Requires staged changes to be present
    and validates git repository state before proceeding.
    Usage: `/commit` -> generates and creates commit with AI-generated message
    """

    @property
    def name(self) -> str:
        return "commit"

    @property
    def description(self) -> str:
        return "Create a git commit with staged changes"

    async def execute(self, args: str) -> None:
        """Generate commit message from staged changes and create commit.

        Validates git repository state, analyzes staged changes, and uses
        the main LLM to generate a conventional commit message before
        creating the actual commit.
        Usage: Called by command processor when user types `/commit`
        """
        commit_service = await self.make(CommitService)
        await commit_service.execute()
