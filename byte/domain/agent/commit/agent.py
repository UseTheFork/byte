from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.domain.agent.base import Agent, BaseState
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

        graph = await self.get_graph()
        return await graph.ainvoke(staged_diff)

    async def build(self) -> "CompiledStateGraph":
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """

        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_weak_model()

        assistant_runnable = commit_prompt | llm
        State = self.get_state_class()

        # Create the state graph with coder-specific state
        graph = StateGraph(State)

        # Add nodes to graph
        graph.add_node("assistant", self._create_assistant_node(assistant_runnable))

        # Set entry point to coder
        graph.add_edge(START, "assistant")
        graph.add_edge("assistant", END)

        # Compile graph with memory and configuration
        return graph.compile(debug=False)

    def _create_assistant_node(self, runnable: Runnable):
        """Create the assistant node function."""

        async def assistant_node(state: BaseState, config: RunnableConfig):
            while True:
                result = await runnable.ainvoke(state, config=config)

                # Ensure we get a real response
                if not result.tool_calls and (
                    not result.content
                    or (
                        isinstance(result.content, list)
                        and not result.content[0].get("text")
                    )
                ):
                    # Re-prompt for actual response
                    messages = state["messages"] + [
                        ("user", "Respond with a real output.")
                    ]
                    state = {**state, "messages": messages}
                else:
                    break

            return {"messages": [result]}

        return assistant_node
