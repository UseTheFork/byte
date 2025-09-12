from ibot import llm
from ibot.prompts import primary_assistant_prompt
from ibot.tools import create_tool_node_with_fallback, search_dcr_information
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import tools_condition


# Credits to: https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/customer-support/customer-support.ipynb
# Useful resource for building the graph.
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: MessagesState, config: RunnableConfig):
        while True:
            # This lets us inject data in to the runable as needed
            # configuration = config.get("configurable", {})
            # passenger_id = configuration.get("passenger_id", None)
            # state = {**state, "user_info": passenger_id}
            state = {**state}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or (
                    isinstance(result.content, list)
                    and not result.content[0].get("text")
                )
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


primary_assistant_assistant_runnable = (
    primary_assistant_prompt | llm.get_llm().bind_tools([search_dcr_information])
)


class StateGraphBuilder:
    def __init__(self, checkpointer):
        self.checkpointer = checkpointer

    def build(self) -> CompiledStateGraph:
        builder = StateGraph(MessagesState)
        builder.add_node("assistant", Assistant(primary_assistant_assistant_runnable))
        builder.add_node(
            "tools", create_tool_node_with_fallback([search_dcr_information])
        )

        builder.add_edge(START, "assistant")
        builder.add_conditional_edges(
            "assistant",
            tools_condition,
        )
        builder.add_edge("tools", "assistant")

        graph = builder.compile(checkpointer=self.checkpointer)

        return graph
