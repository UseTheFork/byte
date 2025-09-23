from typing import Annotated, Type, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.graph.message import AnyMessage
from langgraph.graph.state import CompiledStateGraph

from byte.domain.agent.base import Agent, BaseState
from byte.domain.agent.commit.prompt import commit_prompt
from byte.domain.llm.service.llm_service import LLMService


class ComitState(TypedDict):
    """State for commit agent with message history and extracted content."""

    messages: Annotated[list[AnyMessage], add_messages]
    content: str


class CommitAgent(Agent):
    """Domain service for generating AI-powered git commit messages and creating commits."""

    def get_state_class(self) -> Type[TypedDict]:  # pyright: ignore[reportInvalidTypeForm]
        return ComitState

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
        result = await graph.ainvoke(
            {"messages": [("user", staged_diff)], "content": ""}
        )
        return result.get("content", "")

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
        graph.add_node("extract_commit", self._create_extract_node(assistant_runnable))

        # Set entry point to coder
        graph.add_edge(START, "assistant")
        graph.add_edge("assistant", "extract_commit")
        graph.add_edge("extract_commit", END)

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

    def _create_extract_node(self, runnable: Runnable):
        """Create the extract node that extracts content from the last message."""

        async def extract_node(state: BaseState, config: RunnableConfig):
            # Extract content from the last message in the state
            messages = state.get("messages", [])
            if not messages:
                return {"content": ""}

            last_message = messages[-1]

            # Handle different message formats
            if hasattr(last_message, "content"):
                content = last_message.content
            elif isinstance(last_message, tuple) and len(last_message) > 1:
                content = last_message[1]
            elif isinstance(last_message, dict):
                content = last_message.get("content", "")
            else:
                content = str(last_message)

            # If content is a list (like from some LLM responses), extract text
            if isinstance(content, list) and content:
                if isinstance(content[0], dict) and "text" in content[0]:
                    content = content[0]["text"]
                else:
                    content = str(content[0])

            return {"content": content}

        return extract_node
