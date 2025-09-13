from typing import TYPE_CHECKING

import git
from git.exc import GitCommandError, InvalidGitRepositoryError

from byte.core.command.registry import Command
from byte.domain.commit.prompt import commit_prompt

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from rich.console import Console

    from byte.domain.llm.service import LLMService


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
        console: Console = self.container.make("console")

        try:
            # Initialize git repository with parent directory search
            repo = git.Repo(search_parent_directories=True)

            # Validate staged changes exist to prevent empty commits
            if not repo.index.diff("HEAD"):
                console.print("[warning]No staged changes to commit.[/warning]")
                return

            # Extract staged changes for AI analysis
            staged_diff = repo.git.diff("--cached")

            console.print("[info]Generating commit message...[/info]")

            # Use main model for high-quality commit message generation
            llm_service: LLMService = self.container.make("llm_service")
            llm: BaseChatModel = llm_service.get_main_model()
            result_message = llm.invoke(commit_prompt.invoke({"changes": staged_diff}))

            # Create commit with AI-generated message
            commit = repo.index.commit(result_message.content)
            console.print(
                f"[success]Commit:[/success] [info]{commit.hexsha[:7]}[/info] {commit.message.strip()}"
            )
            return

        except InvalidGitRepositoryError:
            console.print("[error]Error: Not in a git repository[/error]")
            return
        except GitCommandError as e:
            console.print(f"[error]Git commit failed:[/error] {e}")
            return
        except Exception as e:
            console.print(f"[error]Unexpected error:[/error] {e}")
            return
