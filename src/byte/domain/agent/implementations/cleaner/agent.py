from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage
from langgraph.constants import END
from langgraph.graph import START, StateGraph
from langgraph.types import Command
from rich.markdown import Markdown

from byte.core.mixins.user_interactive import UserInteractive
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.cleaner.prompt import cleaner_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.extract_node import ExtractNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.llm.service.llm_service import LLMService


class CleanerAgent(Agent, UserInteractive):
    """Domain service for extracting relevant information from content.

    Processes raw content to extract only essential information for services
    like session context, removing noise and focusing on key details.
    Usage: `agent = await container.make(CleanerAgent); clean = await agent.execute(state)`
    """

    async def build(self):
        """Build and compile the cleaner agent graph.

        Creates a StateGraph optimized for content cleaning with specialized
        prompts focused on information extraction and relevance filtering.
        Usage: `graph = await agent.build()` -> ready for content cleaning
        """

        # Create the state graph
        graph = StateGraph(BaseState)

        # Add nodes
        graph.add_node("start_node", await self.make(StartNode))
        graph.add_node("assistant_node", await self.make(AssistantNode, goto="extract_node"))
        graph.add_node("extract_node", await self.make(ExtractNode))
        graph.add_node("end_node", await self.make(EndNode))

        graph.add_node("confirm_content_node", self._confirm_content)

        # Define edges
        graph.add_edge(START, "start_node")
        graph.add_edge("start_node", "assistant_node")
        graph.add_edge("assistant_node", "extract_node")
        graph.add_edge("extract_node", "confirm_content_node")
        graph.add_edge("confirm_content_node", "end_node")
        graph.add_edge("end_node", END)

        # Compile graph without memory for stateless operation
        return graph.compile()

    async def _confirm_content(self, state: BaseState):
        """Ask user to confirm the cleaned content or provide modifications.

        Displays the extracted content and prompts user to either accept it
        or provide feedback for modification.
        Usage: `result = await agent._confirm_content(state)` -> updated state
        """

        console = await self.make(ConsoleService)

        cleaned_content = state.get("extracted_content", "")

        markdown_rendered = Markdown(cleaned_content)

        console.print_panel(
            markdown_rendered,
            title="Cleaned Content",
        )

        confirmed, user_input = await self.prompt_for_confirm_or_input(
            "Use this cleaned content?",
            "Please provide instructions for how to modify the content:",
            default_confirm=True,
        )

        if confirmed:
            # User accepted the content, proceed to end
            return Command(goto="end_node")
        else:
            # User wants modifications, add their feedback to messages
            error_message = HumanMessage(
                content=f"Please revise the cleaned content based on this feedback: {user_input}"
            )

            return Command(goto="assistant_node", update={"history_messages": [error_message]})

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = await self.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="weak",
            prompt=cleaner_prompt,
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
        )
