from langchain.chat_models import BaseChatModel

from byte.agent import Agent, AssistantContextSchema, AssistantNode, ExtractNode, UserConfirmValidator, ValidationNode
from byte.agent.implementations.cleaner.prompt import cleaner_prompt, cleaner_user_template
from byte.agent.utils.graph_builder import GraphBuilder
from byte.llm import LLMService
from byte.support.mixins import UserInteractive


class CleanerAgent(Agent, UserInteractive):
    """Domain service for extracting relevant information from content.

    Processes raw content to extract only essential information for services
    like session context, removing noise and focusing on key details.
    Usage: `agent = await container.make(CleanerAgent); clean = await agent.execute(state)`
    """

    def get_validators(self):
        return [
            self.app.make(UserConfirmValidator),
        ]

    def get_user_template(self):
        return cleaner_user_template

    def get_prompt(self):
        return cleaner_prompt

    async def build(self):
        """Build and compile the cleaner agent graph.

        Creates a StateGraph optimized for content cleaning with specialized
        prompts focused on information extraction and relevance filtering.
        Usage: `graph = await agent.build()` -> ready for content cleaning
        """

        graph = GraphBuilder(self.app)
        graph.add_node(AssistantNode, goto=ValidationNode)
        graph.add_node(ValidationNode, goto=ExtractNode, validators=self.get_validators())
        graph.add_node(ExtractNode)

        # Compile graph without memory for stateless operation
        return graph.build().compile()

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="weak",
            user_template=self.get_user_template(),
            prompt=self.get_prompt(),
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
        )
