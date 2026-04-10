from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import CompiledStateGraph, RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.git import CommitMessage, CommitValidator
from byte.node import (
    EndNode,
    ModelWeakNode,
    ValidationNode,
)
from byte.orchestration import (
    AssistantContextSchema,
    BaseState,
    GraphBuilder,
)
from byte.subgraph import BaseAgent
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

# Conventional commit message generation prompt
# Adapted from Aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/prompts.py#L8
# Conventional Commits specification: https://www.conventionalcommits.org/en/v1.0.0/#summary

commit_user_template = [
    Boundary.open(BoundaryType.USER_INPUT),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** consider the user input before proceeding (if not empty).",
    Boundary.close(BoundaryType.USER_INPUT),
    "",
    "{masked_messages}",
    "",
    Boundary.open(BoundaryType.TASK),
    "You are an expert software engineer that generates concise, Git commit messages based on the provided diffs.",
    "Review the provided context and diffs which are about to be committed to a git repo.",
    "Review the diffs carefully.",
    Boundary.critical("You MUST follow the commit guidelines provided in the Rules section below."),
    "Read and apply ALL rules for commit types, scopes, and description formatting.",
    Boundary.close(BoundaryType.TASK),
    "{commit_guidelines}",
]


commit_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    "You are an expert software engineer that generates organized Git commits based on the provided user input.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)


class CommitAgent(BaseAgent):
    """ """

    def get_validators(self):
        return [
            self.app.make(CommitValidator),
        ]

    def get_user_template(self):
        return commit_user_template

    def get_prompt(self):
        return commit_prompt

    def get_tools(self):
        return []

    def get_structured_output(self):
        return CommitMessage

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = GraphBuilder(self.app)

        # Add nodes
        graph.add_node(ModelWeakNode, goto=ValidationNode, structured_output=self.get_structured_output())
        graph.add_node(ValidationNode, goto=EndNode, validators=self.get_validators())

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
