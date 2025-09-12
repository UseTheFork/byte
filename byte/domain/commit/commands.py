
import git
import rich
from git.exc import GitCommandError, InvalidGitRepositoryError
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)

from byte.core.command.registry import Command
from byte.domain.commit.prompt import commit_prompt
from byte.domain.llm.service import LLMService


class CommitCommand(Command):
    @property
    def name(self) -> str:
        return "commit"

    @property
    def description(self) -> str:
        return "Create a git commit with staged changes"

    async def execute(self, args: str) -> str:

        # commit_message = args.strip()

        try:
            # Initialize git repository
            repo = git.Repo(search_parent_directories=True)

            # Check if there are staged changes
            if not repo.index.diff("HEAD"):
                return (
                    "No staged changes to commit. Use 'git add' to stage files first."
                )

            # Get the diff of staged changes
            staged_diff = repo.git.diff("--cached")

            llm_service: LLMService = self.container.make("llm_service")
            llm: BaseChatModel = llm_service.get_main_model()
            result_message = llm.invoke(commit_prompt.invoke({"changes": staged_diff}))

            # Create the commit
            commit = repo.index.commit(result_message.text())
            rich.print(f"Commit [{commit.hexsha[:7]}] {commit.message.strip()}")
            return "Commit created successfully:\n"

        except InvalidGitRepositoryError:
            return "Not in a git repository"
        except GitCommandError as e:
            return f"Git commit failed: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
