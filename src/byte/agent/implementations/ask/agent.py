from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph

from byte.agent import Agent, AssistantContextSchema, AssistantNode, BaseState, DummyNode, EndNode, StartNode, ToolNode
from byte.agent.implementations.ask.prompt import ask_enforcement, ask_prompt
from byte.llm import LLMService


class AskAgent(Agent):
    """Domain service for the ask agent specialized in question answering with tools.

    Pure domain service that handles query processing and tool execution without
    UI concerns. Integrates with MCP tools and the LLM service through the actor
    system for clean separation of concerns.

    Usage: `agent = await container.make(AskAgent); response = await agent.run(state)`
    """

    async def build(self):
        """Build and compile the ask agent graph with memory and MCP tools.

        Creates a graph workflow that processes user queries through setup,
        assistant, and tool execution nodes with conditional routing based
        on whether tool calls are required.

        Usage: `graph = await agent.build()`
        """

        # Create the state graph
        graph = StateGraph(BaseState)  # ty:ignore[invalid-argument-type]

        # Add nodes
        graph.add_node("start_node", self.app.make(StartNode))  # ty:ignore[invalid-argument-type]
        graph.add_node("assistant_node", self.app.make(AssistantNode))  # ty:ignore[invalid-argument-type]
        graph.add_node("tools_node", self.app.make(ToolNode))  # ty:ignore[invalid-argument-type]
        graph.add_node("end_node", self.app.make(EndNode))  # ty:ignore[invalid-argument-type]

        graph.add_node("parse_blocks_node", self.app.make(DummyNode))  # ty:ignore[invalid-argument-type]

        # Define edges
        graph.set_entry_point("start_node")
        graph.set_finish_point("end_node")

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        # test: RunnableSerializable[dict[Any, Any], BaseMessage] = ask_prompt | main
        # main.bind_tools(mcp_tools, parallel_tool_calls=False)

        return AssistantContextSchema(
            mode="main",
            prompt=ask_prompt,
            enforcement=ask_enforcement,
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
        )
