from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.files import AddFilesTool, ListFilesTool
from byte.git import GitGrepTool
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AIMessage, BaseState, Leaves
from byte.support import Section, SectionType, Str
from byte.support.utils import extract_content_from_message
from byte.system import UserSelectTool
from byte.web import SearchWebTool


class ResearchAgentNode(BaseAgentNode):
    llm_tier: str = "reasoning"

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

    def get_user_template(self):
        return [
            Leaves.ConversationHistory(),
            Leaves.UserRequest(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role="Act as an expert research analyst specializing in code exploration, analysis, and knowledge synthesis. Your role is to investigate codebases, understand complex systems, and provide clear, evidence-based insights."
            ),
            Leaves.CommunicationStyle(verbose=True),
            Leaves.WorkflowConstraints(
                [
                    "Use search and grep tools to explore the codebase before making claims",
                    "Ground all findings in actual code references (file paths, snippets)",
                    "Respect existing conventions, architectures, and patterns in the codebase",
                    "Ask clarifying questions if the research objective is ambiguous",
                    "Synthesize findings into actionable insights with clear implications",
                    "Do not propose implementation changes unless explicitly requested - focus on analysis and understanding",
                    "For comparative analysis, examine multiple code paths and document trade-offs",
                ]
            ),
            "",
            Section.start(SectionType.RESPONSE_FORMAT),
            "Structure findings with clear headings and sections",
            "Always cite code references (file path, function/class name)",
            "Use code blocks only to highlight key evidence, not full implementations",
            "Provide context explaining why findings matter for the codebase",
            "End with actionable takeaways or recommendations based on evidence",
            Section.end(),
            "",
            Leaves.OperatingPrinciples(),
        ]

    def get_context_template(self):
        return [
            Leaves.ReferenceMaterials(),
            Leaves.ProjectEnvironment(),
            Leaves.ProjectHierarchy(),
            Leaves.HarnessWorkspaceFiles(),
            Leaves.HarnessWorkspaceReferenceFiles(),
            Leaves.Epilogue(
                enforcements=[
                    "NEVER use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
                    "Always use the GitGrepTool and ListFilesTool to explore the codebase and ground your analysis in actual code.",
                    "Prioritize evidence-based findings over assumptions—verify claims with code references.",
                ]
            ),
        ]

    def get_tools(self, state: BaseState):
        return [
            GitGrepTool,
            ListFilesTool,
            SearchWebTool,
            UserSelectTool,
            AddFilesTool,
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        prompt_assembler = await self.generate_agent_state(state, config)
        prompt = await self.generate_prompt(prompt_assembler)
        runnable = self.create_runnable(prompt_assembler)

        result = await runnable.ainvoke(
            prompt,
            config=config,
            cache_control={"type": "ephemeral"},
        )
        await self.finalize_response(result, prompt, config)

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": AIMessage(content=msg, agent_name=self.human_name)})
