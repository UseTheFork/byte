from langchain.chat_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph

from byte.agent import (
    Agent,
    AssistantContextSchema,
    AssistantNode,
    LintNode,
    ParseBlocksNode,
    ToolNode,
)
from byte.agent.implementations.coder.prompt import coder_prompt, coder_user_template
from byte.agent.utils.graph_builder import GraphBuilder
from byte.conventions import load_conventions
from byte.llm import LLMService
from byte.prompt_format import EditFormatService


class CoderAgent(Agent):
    """Domain service for the coder agent specialized in software development.

    Pure domain service that handles coding logic without UI concerns.
    Integrates with file context, memory, and development tools through
    the actor system for clean separation of concerns.
    """

    def get_enforcement(self):
        edit_format_service = self.app.make(EditFormatService)
        return edit_format_service.prompts.enforcement

    def get_recovery_steps(self):
        edit_format_service = self.app.make(EditFormatService)
        return edit_format_service.prompts.recovery_steps

    def get_user_template(self):
        return coder_user_template

    def get_prompt(self):
        return coder_prompt

    def get_tools(self):
        return [load_conventions]

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = GraphBuilder(self.app)

        # Add nodes
        graph.add_node(AssistantNode, goto="parse_blocks_node")
        graph.add_node(ParseBlocksNode)
        graph.add_node(LintNode)
        graph.add_node(ToolNode)

        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="main",
            prompt=self.get_prompt(),
            user_template=self.get_user_template(),
            main=main,
            weak=weak,
            enforcement=self.get_enforcement(),
            recovery_steps=self.get_recovery_steps(),
            agent=self.__class__.__name__,
            tools=self.get_tools(),
        )
