from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.constants import END
from langgraph.graph import START, StateGraph

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.conventions.prompt import conventions_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.extract_node import ExtractNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.nodes.tool_node import ToolNode
from byte.domain.agent.nodes.validation_node import ValidationNode
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.files.tools.read_files import read_files
from byte.domain.llm.service.llm_service import LLMService


class ConventionAgent(Agent):
    """Agent for generating project convention documents by analyzing codebase patterns.

    Analyzes the codebase to extract and document conventions such as style guides,
    architecture patterns, comment standards, and code patterns. Uses validation
    to ensure generated conventions meet quality standards before extraction.
    Usage: `agent = await container.make(ConventionAgent); result = await agent.execute(request)`
    """

    # Convention agent dosent use or update the main memory.
    async def get_checkpointer(self):
        return None

    def get_tools(self):
        return [read_files]

    async def build(self):
        """Build and compile the convention agent graph with validation and extraction.

        Creates a graph that processes user requests through the assistant, validates
        the response against constraints (e.g., max lines), and extracts the formatted
        convention document for saving to the conventions directory.

        Returns:
                CompiledStateGraph ready for execution

        Usage: `graph = await agent.build()` -> returns compiled graph
        """

        # Create the state graph
        graph = StateGraph(BaseState)

        # Add nodes
        graph.add_node("start_node", await self.make(StartNode))
        graph.add_node("assistant_node", await self.make(AssistantNode, goto="validation_node"))
        graph.add_node(
            "validation_node",
            await self.make(
                ValidationNode,
                goto="extract_node",
                max_lines=75,
            ),
        )

        graph.add_node("extract_node", await self.make(ExtractNode))
        graph.add_node("tools_node", await self.make(ToolNode))
        graph.add_node("end_node", await self.make(EndNode))

        # Define edges
        graph.add_edge(START, "start_node")
        graph.add_edge("start_node", "assistant_node")
        graph.add_edge("end_node", END)

        # Compile graph with memory and configuration
        return graph.compile()

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = await self.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="main",
            prompt=conventions_prompt,
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
            tools=self.get_tools(),
        )
