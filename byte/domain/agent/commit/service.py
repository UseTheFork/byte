from typing import TYPE_CHECKING

import git
from git.exc import GitCommandError, InvalidGitRepositoryError
from langgraph.graph import END, START, StateGraph

from byte.context import make
from byte.core.response.handler import ResponseHandler
from byte.domain.agent.base import BaseAgentService, BaseAssistant
from byte.domain.agent.commit.events import CommitCreated, PreCommitStarted
from byte.domain.agent.commit.prompt import commit_prompt
from byte.domain.ui.interactions import InteractionService

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langgraph.graph.state import CompiledStateGraph
    from rich.console import Console

    from byte.domain.llm.service import LLMService


class CommitService(BaseAgentService):
    """Domain service for generating AI-powered git commit messages and creating commits."""

    async def _handle_unstaged_changes(self, repo, console) -> None:
        """Check for unstaged changes and offer to add them to the commit.

        Args:
            repo: Git repository instance
            console: Rich console for output

        Usage: Called internally during commit process to handle unstaged files
        """
        unstaged_changes = repo.index.diff(None)  # None compares working tree to index
        if unstaged_changes:
            interaction_service = await make(InteractionService)
            should_add = await interaction_service.confirm(
                f"Found {len(unstaged_changes)} unstaged changes. Add them to this commit?",
                default=True,
            )
            if should_add:
                # Add all unstaged changes
                repo.git.add("--all")
                console.print(
                    f"[info]Added {len(unstaged_changes)} unstaged changes[/info]"
                )

    async def execute(self) -> None:
        """Generate commit message from staged changes and create commit.

        Validates git repository state, analyzes staged changes, and uses
        the main LLM to generate a conventional commit message before
        creating the actual commit.
        Usage: Called by command processor when user types `/commit`
        """
        console = await make(Console)

        try:
            # Initialize git repository with parent directory search
            repo = git.Repo(search_parent_directories=True)

            # Check for unstaged changes and offer to add them
            await self._handle_unstaged_changes(repo, console)

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

            response_handler = await make(ResponseHandler)

            result_message = await response_handler.handle_stream(
                self.stream(staged_diff)
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

    async def build(self) -> "CompiledStateGraph":
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """

        llm_service = await make(LLMService)
        llm: BaseChatModel = llm_service.get_weak_model()

        assistant_runnable = commit_prompt | llm
        State = self.get_state_class()

        # Create the state graph with coder-specific state
        graph = StateGraph(State)

        # Add nodes to graph
        graph.add_node("agent", BaseAssistant(assistant_runnable))

        # Set entry point to coder
        graph.add_edge(START, "agent")
        graph.add_edge("agent", END)

        # Compile graph with memory and configuration
        return graph.compile(debug=False)
