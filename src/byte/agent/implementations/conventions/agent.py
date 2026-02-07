from langchain_core.language_models.chat_models import BaseChatModel

from byte.agent import (
    Agent,
    AssistantContextSchema,
    AssistantNode,
    ExtractNode,
    PromptSettingsSchema,
    ToolNode,
    ValidationNode,
)
from byte.agent.implementations.conventions.prompt import conventions_prompt, conventions_user_template
from byte.agent.utils.graph_builder import GraphBuilder
from byte.files.tools.read_files import read_files
from byte.llm import LLMService
from byte.parsing import ConventionValidator


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

    def get_user_template(self):
        return conventions_user_template

    def get_prompt(self):
        return conventions_prompt

    def get_tools(self):
        return [read_files]

    def get_validators(self):
        return [
            self.app.make(ConventionValidator),
        ]

    async def build(self):
        """Build and compile the convention agent graph with validation and extraction.

        Creates a graph that processes user requests through the assistant, validates
        the response against constraints (e.g., max lines), and extracts the formatted
        convention document for saving to the conventions directory.

        Returns:
                CompiledStateGraph ready for execution

        Usage: `graph = await agent.build()` -> returns compiled graph
        """

        graph = GraphBuilder(self.app)

        graph.add_node(AssistantNode, goto=ValidationNode)
        graph.add_node(ValidationNode, goto=ExtractNode, validators=self.get_validators())
        graph.add_node(ExtractNode)
        graph.add_node(ToolNode)

        return graph.build().compile()

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="main",
            user_template=self.get_user_template(),
            prompt=self.get_prompt(),
            prompt_settings=PromptSettingsSchema(
                has_project_hierarchy=True,
            ),
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
            tools=self.get_tools(),
        )
