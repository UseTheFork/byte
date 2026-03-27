from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.conventions import load_convention
from byte.git import git_grep
from byte.node import (
    ModelMainNode,
    ToolNode,
)
from byte.orchestration import (
    AssistantContextSchema,
    BaseState,
    GraphBuilder,
    preamble,
)
from byte.subgraph import BaseAgent
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

ask_user_template = [
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
    "- If the request is ambiguous, ask questions",
    "- Keep changes simple don't build more then what is asked for",
    "- Never use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
    "- Do not provide full code implementations unless explicitly requested. Describe the changes needed first.",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "- Use clear, concise explanations",
    "- Format code with proper syntax highlighting",
    "- Provide context for suggested changes",
    "- Focus on actionable findings, not exhaustive documentation",
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    "{available_conventions}",
    "{project_hierarchy}",
    "{project_information_and_context}",
    "{file_context}",
    "{operating_principles}",
]

ask_prompt = ChatPromptTemplate.from_messages(
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
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
    ]
)

ask_enforcement = [
    "- NEVER use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
    "- DO NOT provide full code implementations unless explicitly requested. Describe the changes needed first.",
]


class AskAgent(BaseAgent):
    def get_enforcement(self):
        return ask_enforcement

    def get_user_template(self):
        return ask_user_template

    def get_prompt(self):
        return ask_prompt

    def get_tools(self):
        return [load_convention, git_grep]

    async def build(self):
        """Build and compile the ask agent graph with memory and MCP tools.

        Creates a graph workflow that processes user queries through setup,
        assistant, and tool execution nodes with conditional routing based
        on whether tool calls are required.

        Usage: `graph = await agent.build()`
        """

        graph = GraphBuilder(self.app, start_node=ModelMainNode)

        # Add nodes
        graph.add_node(ModelMainNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        assistant_context_schema = AssistantContextSchema(
            mode="main",
            prompt=self.get_prompt(),
            user_template=self.get_user_template(),
            enforcement=self.get_enforcement(),
            agent=self.__class__.__name__,
            tools=self.get_tools(),
        )

        return assistant_context_schema

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["routing_node"]]:
        subgraph = await self.get_graph()

        state["agent"] = self.get_node_name()
        subgraph_output = await subgraph.ainvoke(
            input=state,
            context=await self.get_assistant_runnable(),  # ty:ignore[invalid-argument-type]
        )

        return Command(
            goto="routing_node",
            update={
                "node_to": "end_node",
                "node_from": self.get_node_name(),
                "scratch_messages": [subgraph_output["final_message"]],
            },
        )
