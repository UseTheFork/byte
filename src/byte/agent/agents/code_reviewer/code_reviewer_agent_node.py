from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import (
    AssistantContextSchema,
    BaseAgentNode,
    BaseState,
    ReasoningModelNode,
    RoutingNode,
    ToolNode,
)
from byte.agent.prompt_leaves import preamble
from byte.agent.utils.graph_builder import GraphBuilder
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

code_reviewer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    preamble(),
                    "Act as a Senior Code Reviewer with expertise in software architecture, design patterns, and best practices. Your role is to review completed project steps against original plans and ensure code quality standards are met.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
    ]
)

code_reviewer_user_template = [
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


class CodeReviewerAgentNode(BaseAgentNode):
    def get_prompt(self):
        return code_reviewer_prompt

    def get_user_template(self):
        return code_reviewer_user_template

    async def build(self):
        """Build and compile the ask agent graph with memory and MCP tools.

        Creates a graph workflow that processes user queries through setup,
        assistant, and tool execution nodes with conditional routing based
        on whether tool calls are required.

        Usage: `graph = await agent.build()`
        """

        graph = GraphBuilder(self.app)

        # Add nodes
        graph.add_node(ReasoningModelNode)
        graph.add_node(RoutingNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        assistant_context_schema = AssistantContextSchema(
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

        subgraph_output = subgraph.invoke(state)

        return Command(
            goto="routing_node",
            update={
                "node_to": "",
                "node_from": self.get_node_name(),
                "scratch_messages": subgraph_output,
                "errors": None,
            },
        )
