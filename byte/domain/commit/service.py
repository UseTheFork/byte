from typing import TYPE_CHECKING

import git
from git.exc import GitCommandError, InvalidGitRepositoryError

from byte.context import make
from byte.core.config.mixins import Configurable
from byte.core.events.mixins import Eventable
from byte.core.service.mixins import Bootable
from byte.domain.commit.events import CommitCreated, PreCommitStarted
from byte.domain.commit.prompt import commit_prompt

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from rich.console import Console

    from byte.domain.llm.service import LLMService


class CommitService(Bootable, Configurable, Eventable):
    """Domain service for generating AI-powered git commit messages and creating commits."""

    async def execute(self) -> None:
        """Generate commit message from staged changes and create commit.

        Validates git repository state, analyzes staged changes, and uses
        the main LLM to generate a conventional commit message before
        creating the actual commit.
        Usage: Called by command processor when user types `/commit`
        """
        console: Console = await make("console")

        try:
            # Initialize git repository with parent directory search
            repo = git.Repo(search_parent_directories=True)

            # Validate staged changes exist to prevent empty commits
            if not repo.index.diff("HEAD"):
                console.print("[warning]No staged changes to commit.[/warning]")
                return

            # Extract staged changes for AI analysis
            staged_diff = repo.git.diff("--cached")

            # Emit pre-commit event for other domains to react
            await self.event(
                PreCommitStarted(
                    staged_files=len(repo.index.diff("HEAD")),
                    diff_size=len(staged_diff),
                )
            )

            console.print("[info]Generating commit message...[/info]")

            # Use main model for high-quality commit message generation
            llm_service: LLMService = await make("llm_service")
            llm: BaseChatModel = llm_service.get_weak_model()

            result_message = await llm.ainvoke(
                await commit_prompt.ainvoke({"changes": staged_diff})
            )

            # Create commit with AI-generated message
            commit = repo.index.commit(result_message.content)

            # Emit event for other domains to react to the commit
            await self.event(
                CommitCreated(
                    commit_hash=commit.hexsha,
                    message=commit.message.strip(),
                    files_changed=len(repo.index.diff("HEAD~1")),
                )
            )

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
