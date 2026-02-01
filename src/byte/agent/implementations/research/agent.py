from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph

from byte.agent import (
    Agent,
    AssistantContextSchema,
    AssistantNode,
    ExtractNode,
    ToolNode,
)
from byte.agent.implementations.research.prompt import research_prompt, research_user_template
from byte.agent.utils.graph_builder import GraphBuilder
from byte.llm import LLMService
from byte.lsp.tools.find_references import find_references
from byte.lsp.tools.get_definition import get_definition
from byte.lsp.tools.get_hover_info import get_hover_info


class ResearchAgent(Agent):
    """Domain service for AI-powered code research and information gathering.

    Extends Agent to provide research capabilities with tool execution for
    file searching and reading. Integrates with MCP services for extended
    tool availability and uses ripgrep for fast codebase searches.
    Usage: `agent = await container.make(ResearchAgent); result = await agent.execute(state)`
    """

    # Research agent dosent use or update the main memory even thou it gets the current checkpointer state.
    async def get_checkpointer(self):
        return None

    def get_tools(self):
        return [find_references, get_definition, get_hover_info]
        # return [ripgrep_search, read_file]

    def get_user_template(self):
        return research_user_template

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = GraphBuilder(self.app)
        graph.add_node(AssistantNode, goto=ExtractNode)
        graph.add_node(ExtractNode, schema="session_context")
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="main",
            user_template=self.get_user_template(),
            prompt=research_prompt,
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
            tools=self.get_tools(),
        )
