from langchain_core.language_models.chat_models import BaseChatModel

from byte.domain.agent.base import Agent
from byte.domain.agent.commit.prompt import commit_prompt
from byte.domain.llm.service.llm_service import LLMService


class CommitAgent(Agent):
    """Domain service for generating AI-powered git commit messages and creating commits."""

    async def execute(self, staged_diff: str):
        """Generate an AI-powered commit message from staged git changes.

        Analyzes the provided git diff to understand the changes and generates
        a concise, conventional commit message that accurately describes the
        modifications made to the codebase.

        Args:
            staged_diff: Git diff output showing staged changes to be committed

        Returns:
            Generated commit message following conventional commit format

        Usage: `message = await commit_agent.execute(git_diff_output)` -> "feat: add user authentication"
        """

        graph = await self.get_agent()
        result = await graph.ainvoke(
            {"messages": [("user", staged_diff)], "content": ""}
        )
        return result.get("content", "")

    async def build(self):
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """

        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_weak_model()

        assistant_runnable = commit_prompt | llm

        # Compile graph with memory and configuration
        return assistant_runnable
