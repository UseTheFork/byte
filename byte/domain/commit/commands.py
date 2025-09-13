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
    @property
    def name(self) -> str:
        return "commit"

    @property
    def description(self) -> str:
        return "Create a git commit with staged changes"

    async def execute(self, args: str) -> None:
        console: Console = self.container.make("console")

        try:
            # Initialize git repository
            repo = git.Repo(search_parent_directories=True)

            # Check if there are staged changes
            if not repo.index.diff("HEAD"):
                console.print("[yellow]No staged changes to commit.[/yellow]")
                return

            # Get the diff of staged changes
            staged_diff = repo.git.diff("--cached")

            console.print("[blue]Generating commit message...[/blue]")

            llm_service: LLMService = self.container.make("llm_service")
            llm: BaseChatModel = llm_service.get_main_model()
            result_message = llm.invoke(commit_prompt.invoke({"changes": staged_diff}))

            # Create the commit
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
