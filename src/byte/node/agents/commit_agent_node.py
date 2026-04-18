from typing import Literal, Type

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.git import CommitMessage
from byte.llm import LLMService
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AssistantContextSchema, BaseState
from byte.support import Boundary, BoundaryType, Str
from byte.support.utils import list_to_multiline_text
from byte.tui import Messages

# Conventional commit message generation prompt
# Adapted from Aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/prompts.py#L8
# Conventional Commits specification: https://www.conventionalcommits.org/en/v1.0.0/#summary

commit_user_template = [
    Boundary.open(BoundaryType.GIT_CONTEXT),
    "{user_request}",
    "",
    "You **MUST** consider the above git diffs before proceeding (if not empty).",
    Boundary.close(BoundaryType.GIT_CONTEXT),
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


class CommitAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        """Initialize the validation node with constraints and routing configuration.

        Args:
                goto: Next node to route to after successful validation (default: "end_node")
                max_lines: Maximum number of non-blank lines allowed in response content (optional)

        Usage: `await node.boot(goto="end_node", max_lines=100)`
        """

        self.goto = Str.class_to_snake_case(goto)

    def get_model(self) -> BaseChatModel:
        llm_service = self.app.make(LLMService)
        return llm_service.get_weak_model()

    def get_prompt(self):
        return commit_prompt

    def get_user_template(self):
        return commit_user_template

    def get_structured_output(self):
        return CommitMessage

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        agent_state, config = await self.generate_agent_state(state, config, runtime.context)
        runnable = self.create_runnable()
        record_response_service = self.app.make(RecordResponseService)

        await self.emit_tui(Messages.LoadingIndicatorShow())
        await self.emit_tui(Messages.AddHeading("Commit Agent", "text-primary"))
        await self.emit_tui(Messages.ResponseStarted())

        result = await runnable.ainvoke(agent_state, config=config)
        await record_response_service.record_response(agent_state, runnable, "commit_agent", config)

        await self.emit_tui(Messages.ResponseComplete())
        await self.emit_tui(Messages.LoadingIndicatorHide())

        return self.route_to(self.goto, {"extracted_content": result, "errors": None})
