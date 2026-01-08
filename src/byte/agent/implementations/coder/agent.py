from langchain.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.agent import (
    Agent,
    AssistantContextSchema,
    AssistantNode,
    BaseState,
    EndNode,
    LintNode,
    ParseBlocksNode,
    StartNode,
)
from byte.agent.implementations.coder.prompt import coder_prompt
from byte.llm import LLMService
from byte.prompt_format import EditFormatService


class CoderAgent(Agent):
    """Domain service for the coder agent specialized in software development.

    Pure domain service that handles coding logic without UI concerns.
    Integrates with file context, memory, and development tools through
    the actor system for clean separation of concerns.
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        # Create the state graph
        graph = StateGraph(BaseState)

        # Add nodes
        graph.add_node("start_node", self.app.make(StartNode))
        graph.add_node("assistant_node", self.app.make(AssistantNode, goto="parse_blocks_node"))
        graph.add_node("parse_blocks_node", self.app.make(ParseBlocksNode))
        graph.add_node("lint_node", self.app.make(LintNode))
        graph.add_node("end_node", self.app.make(EndNode))

        # Define edges
        graph.add_edge(START, "start_node")
        graph.add_edge("start_node", "assistant_node")
        graph.add_edge("assistant_node", "parse_blocks_node")

        graph.add_edge("lint_node", "end_node")
        graph.add_edge("end_node", END)

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        edit_format_service = self.make(EditFormatService)

        return AssistantContextSchema(
            mode="main",
            prompt=coder_prompt,
            main=main,
            weak=weak,
            enforcement=edit_format_service.prompts.enforcement,
            recovery_steps=edit_format_service.prompts.recovery_steps,
            agent=self.__class__.__name__,
        )
