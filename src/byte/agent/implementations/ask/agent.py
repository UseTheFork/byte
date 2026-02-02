from langchain_core.language_models.chat_models import BaseChatModel

from byte.agent import Agent, AgentConfigBoolSchema, AssistantContextSchema, AssistantNode, ToolNode
from byte.agent.implementations.ask.prompt import ask_enforcement, ask_prompt, ask_user_template
from byte.agent.utils.graph_builder import GraphBuilder
from byte.llm import LLMService


class AskAgent(Agent):
    """Domain service for the ask agent specialized in question answering with tools.

    Pure domain service that handles query processing and tool execution without
    UI concerns. Integrates with MCP tools and the LLM service through the actor
    system for clean separation of concerns.

    Usage: `agent = await container.make(AskAgent); response = await agent.run(state)`
    """

    def boot_configurable(self, **kwargs):
        self.config().set(
            {
                "has_project_hierarchy": AgentConfigBoolSchema(
                    name="Project Hierarchy",
                    description="Include project directory structure in prompts?",
                    value=False,
                ),
            }
        )

    def get_enforcement(self):
        return ask_enforcement

    def get_user_template(self):
        return ask_user_template

    def get_prompt(self):
        return ask_prompt

    async def build(self):
        """Build and compile the ask agent graph with memory and MCP tools.

        Creates a graph workflow that processes user queries through setup,
        assistant, and tool execution nodes with conditional routing based
        on whether tool calls are required.

        Usage: `graph = await agent.build()`
        """

        graph = GraphBuilder(self.app)

        # Add nodes
        graph.add_node(AssistantNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        # test: RunnableSerializable[dict[Any, Any], BaseMessage] = ask_prompt | main
        # main.bind_tools(mcp_tools, parallel_tool_calls=False)

        assistant_context_schema = AssistantContextSchema(
            mode="main",
            prompt=self.get_prompt(),
            user_template=self.get_user_template(),
            enforcement=self.get_enforcement(),
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
        )

        # Get the config schema object and check its value
        has_hierarchy_config = self.config().get("has_project_hierarchy")
        if has_hierarchy_config and isinstance(has_hierarchy_config, AgentConfigBoolSchema):
            assistant_context_schema.prompt_settings.has_project_hierarchy = has_hierarchy_config.value

        return assistant_context_schema
