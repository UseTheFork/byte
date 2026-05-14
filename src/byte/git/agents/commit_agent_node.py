from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.git import CommitService, GitCommitTool
from byte.llm import LLMService, ModelSchema
from byte.memory import CompleteSimpleTurnTool
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AIMessage, BaseState, Leaves
from byte.support import Boundary, BoundaryType, Section, SectionType, State, Str

# Conventional commit message generation prompt
# Adapted from Aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/prompts.py#L8
# Conventional Commits specification: https://www.conventionalcommits.org/en/v1.0.0/#summary


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

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_user_template(self):
        return [
            Section.sub_heading("Git Diffs", 2),
            "```",
            "{git_diffs}",
            "```",
            Section.important("You **MUST** consider the above git diffs before proceeding (if not empty)."),
            Section.end(),
            Leaves.ConversationHistory(),
            Leaves.CommitHistory(),
            "",
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                "You are an expert software engineer that generates organized Git commits based on the provided user input."
            ),
            Section.start(SectionType.TASK),
            "You are an expert software engineer that generates concise, Git commit messages based on the provided diffs.",
            "Review the provided context and diffs which are about to be committed to a git repo.",
            "Review the diffs carefully.",
            Section.important("You MUST follow the commit guidelines provided in the Rules section below."),
            "Read and apply ALL rules for commit types, scopes, and description formatting.",
            Section.end(),
            Section.start(SectionType.COMMUNICATION_STYLE),
            "- ALWAYS think and respond in the same spoken language the prompt was written in.",
            "- Conciseness is about **text only**: always fully implement the requested feature, tests, and wiring even if that requires many tool calls.",
            """- No preamble ("Here's...", "I'll...")""",
            """- No postamble ("Let me know...", "Hope this helps...")""",
            "- No emojis ever",
            "- No explanations unless user asks",
            "- Never send acknowledgement-only responses; after receiving new context or instructions, immediately continue the task or state the concrete next action you will take.",
            Section.end(),
            Leaves.CommitGuidelines(),
            "",
            Section.start(SectionType.WORKFLOW),
            "Format your response as follows:",
            "",
            "1. Start with a SHORT analysis of the changes in list format.",
            f"2. Call the `{GitCommitTool.name}` tool ONCE.",
            f"3. If the `{GitCommitTool.name}` call is successful, use the `{CompleteSimpleTurnTool.name}`",
            Section.end(),
            Section.sub_heading("Example Workflow", 2),
            "```",
            Boundary.open(BoundaryType.EXAMPLE),
            Boundary.open(BoundaryType.AGENT_MESSAGE),
            "Analysis of changes:",
            "- Updated foo() to handle edge case",
            Boundary.close(BoundaryType.AGENT_MESSAGE),
            Boundary.open(BoundaryType.TOOL_CALL),
            f"{GitCommitTool.name}([removed for brevity])",
            Boundary.close(BoundaryType.TOOL_CALL),
            Boundary.open(BoundaryType.TOOL_CALL),
            f"{CompleteSimpleTurnTool.name}([removed for brevity])",
            Boundary.close(BoundaryType.TOOL_CALL),
            Boundary.close(BoundaryType.EXAMPLE),
            "```",
        ]

    def get_context_template(self):
        return [
            Leaves.ToolsLoaded(),
            Leaves.Epilogue(),
        ]

    def get_tools(self, state: BaseState):
        if not State.tool_was_called(state, GitCommitTool.name):
            return [GitCommitTool]
        else:
            return [CompleteSimpleTurnTool]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        commit_service = self.app.make(CommitService)
        request = await commit_service.build_commit_prompt()

        agent_state, config, prompt_assembler = await self.generate_agent_state(state, config, request)
        runnable = self.create_runnable(prompt_assembler, "any")
        prompt = await self.generate_prompt(prompt_assembler)

        record_response_service = self.app.make(RecordResponseService)

        result = await runnable.ainvoke(prompt, config=config)
        self.app.dispatch_task(
            record_response_service.record_response(prompt, self.name, config),
        )

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        return self.route_to(self.goto, {"scratch_messages": AIMessage(content=result.text, agent_name=self.name)})
