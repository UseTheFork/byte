from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage
from langgraph.types import Command
from rich.markdown import Markdown

from byte.agent import Agent, AssistantContextSchema, AssistantNode, BaseState, ExtractNode
from byte.agent.implementations.cleaner.prompt import cleaner_prompt
from byte.agent.utils.graph_builder import GraphBuilder
from byte.llm import LLMService
from byte.support.mixins import UserInteractive


class CleanerAgent(Agent, UserInteractive):
    """Domain service for extracting relevant information from content.

    Processes raw content to extract only essential information for services
    like session context, removing noise and focusing on key details.
    Usage: `agent = await container.make(CleanerAgent); clean = await agent.execute(state)`
    """

    async def _confirm_content(self, state: BaseState):
        """Ask user to confirm the cleaned content or provide modifications.

        Displays the extracted content and prompts user to either accept it
        or provide feedback for modification.
        Usage: `result = await agent._confirm_content(state)` -> updated state
        """

        console = self.app["console"]

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

    async def build(self):
        """Build and compile the cleaner agent graph.

        Creates a StateGraph optimized for content cleaning with specialized
        prompts focused on information extraction and relevance filtering.
        Usage: `graph = await agent.build()` -> ready for content cleaning
        """

        graph = GraphBuilder(self.app)
        graph.add_node(AssistantNode, goto=ExtractNode)
        graph.add_node(ExtractNode)

        # graph.add_node("confirm_content_node", self._confirm_content)

        # Compile graph without memory for stateless operation
        return graph.build().compile()

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="weak",
            prompt=cleaner_prompt,
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
        )
