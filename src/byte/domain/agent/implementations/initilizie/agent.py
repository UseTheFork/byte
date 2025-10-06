from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.initilizie.prompts import initilizie_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.nodes.tool_node import ToolNode
from byte.domain.agent.state import BaseState
from byte.domain.edit_format.service.edit_format_service import EditFormatService
from byte.domain.llm.service.llm_service import LLMService
from byte.domain.tools.read_file import read_file


class InitilizieAgent(Agent):
    """ """

    edit_format: EditFormatService

    async def boot(self):
        self.edit_format = await self.make(EditFormatService)

    def get_tools(self):
        return [read_file]

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        # Create the assistant and runnable
        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()
        assistant_runnable = initilizie_prompt | llm.bind_tools(self.get_tools())

        # Create the state graph
        graph = StateGraph(self.get_state_class())

        # Add nodes
        graph.add_node(
            "start",
            await self.make(
                StartNode,
                agent=self.__class__.__name__,
                edit_format=self.edit_format,
            ),
        )

        graph.add_node(
            "assistant",
            await self.make(AssistantNode, runnable=assistant_runnable),
        )
        graph.add_node("tools", await self.make(ToolNode, tools=self.get_tools()))

        graph.add_node(
            "end",
            await self.make(
                EndNode,
                agent=self.__class__.__name__,
                llm=llm,
            ),
        )

        # Define edges
        graph.add_edge(START, "start")
        graph.add_edge("start", "assistant")
        graph.add_edge("assistant", "end")

        # Conditional routing from assistant
        graph.add_conditional_edges(
            "assistant",
            self.route_tools,
            {"tools": "tools", "end": "end"},
        )

        graph.add_edge("tools", "assistant")
        graph.add_edge("end", END)

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer, debug=False)

    def route_tools(
        self,
        state: BaseState,
    ):
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")

        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "end"
