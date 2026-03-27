from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import CompiledStateGraph, RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.code_operations import edit_block_enforcement
from byte.conventions import load_convention
from byte.node import LintNode, ModelMainNode, ParseBlocksNode, ToolNode
from byte.orchestration import AssistantContextSchema, BaseState, GraphBuilder, preamble
from byte.subgraph import BaseAgent
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

coder_user_template = [
    "{masked_messages}",
    Boundary.open(BoundaryType.USER_INPUT),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** consider the user input before proceeding (if not empty).",
    Boundary.close(BoundaryType.USER_INPUT),
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- Always use best practices when coding",
    "- Respect and use existing conventions, libraries, etc that are already present in the code base",
    "- Take requests for changes to the supplied code",
    "- If the request is ambiguous, ask clarifying questions before proceeding",
    "- Keep changes simple don't build more then what is asked for",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "{available_conventions}",
    "{project_hierarchy}",
    "{project_information_and_context}",
    "{file_context}",
    "{operating_principles}",
]

coder_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    preamble(),
                    "Act as an expert software developer.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("placeholder", "{examples}"),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)


class CoderAgent(BaseAgent):
    """Domain service for the coder agent specialized in software development.

    Pure domain service that handles coding logic without UI concerns.
    Integrates with file context, memory, and development tools through
    the actor system for clean separation of concerns.
    """

    def get_enforcement(self):
        return edit_block_enforcement

    def get_user_template(self):
        return coder_user_template

    def get_prompt(self):
        return coder_prompt

    def get_tools(self):
        return [load_convention]

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = GraphBuilder(self.app)

        # Add nodes
        graph.add_node(ModelMainNode, goto="parse_blocks_node")
        graph.add_node(ParseBlocksNode)
        graph.add_node(LintNode)
        graph.add_node(ToolNode)

        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        return AssistantContextSchema(
            mode="main",
            prompt=self.get_prompt(),
            user_template=self.get_user_template(),
            enforcement=self.get_enforcement(),
            agent=self.__class__.__name__,
            tools=self.get_tools(),
        )

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["routing_node"]]:
        subgraph = await self.get_graph()

        state["agent"] = self.get_node_name()
        subgraph_output = await subgraph.ainvoke(
            input=state,
            context=await self.get_assistant_runnable(),  # ty:ignore[invalid-argument-type]
        )

        return self.route_to(
            "end_node",
            {
                "scratch_messages": [subgraph_output["final_message"]],
            },
        )
