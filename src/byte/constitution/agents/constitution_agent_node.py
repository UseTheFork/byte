from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.constitution import (
    AddGovernanceRuleTool,
    AddPrincipleTool,
    AddSectionItemTool,
    DeleteGovernanceRuleTool,
    DeletePrincipleTool,
    DeleteSectionItemTool,
    DeleteSectionTool,
    UpdateMetaTool,
)
from byte.development import RecordResponseService
from byte.files import AddFilesTool, ListFilesTool
from byte.git import GitGrepTool
from byte.llm import LLMService, ModelSchema
from byte.memory import ProceedToNextStepTool
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AIMessage, BaseState, Leaves
from byte.support import Section, SectionType, State, Str
from byte.support.utils import extract_content_from_message
from byte.system import UserSelectTool


class ConstitutionAgentNode(BaseAgentNode):
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
            Leaves.UserRequest(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role=f"You are updating the project constitution at {Section.ref(SectionType.CONSTITUTION)}. Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts."
            ),
            "",
            Section.start(SectionType.WORKFLOW),
            f"1. Consider the existing constitution at {Section.ref(SectionType.CONSTITUTION)}",
            Section.important(
                "The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly."
            ),
            "",
            "2. Collect/derive values for placeholders:",
            "   - If user input (conversation) supplies a value, use it.",
            "   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).",
            "   - For governance dates: `RATIFICATION_DATE` is the original adoption date, `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.",
            "   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:",
            "     - MAJOR: Backward incompatible governance/principle removals or redefinitions.",
            "     - MINOR: New principle/section added or materially expanded guidance.",
            "     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.",
            "   - If version bump type ambiguous, propose reasoning before finalizing.",
            "",
            "3. Draft the updated constitution content:",
            "   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet - explicitly justify any left).",
            "   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.",
            "   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non-negotiable rules, explicit rationale if not obvious.",
            "   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.",
            f"  - Use the `{ProceedToNextStepTool.name}` tool to confirm and get access to the tools needed to make the final edits.",
            "",
            "4. Validation before final output:",
            "   - No remaining unexplained bracket tokens.",
            "   - Version line matches report.",
            '   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).',
            "",
            "4. Write the completed constitution using the provided tools.",
            Section.end(),
            "",
            Leaves.OperatingPrinciples(),
        ]

    def get_context_template(self):
        return [
            Leaves.Constitution(),
            Leaves.ToolsLoaded(),
            Leaves.ReferenceMaterials(),
            Leaves.ProjectEnvironment(),
            Leaves.FileContext(),
            Leaves.Epilogue(),
        ]

    def get_tools(self, state: BaseState):

        if State.tool_was_called(state, ProceedToNextStepTool.name):
            return [
                AddGovernanceRuleTool,
                AddPrincipleTool,
                AddSectionItemTool,
                DeleteGovernanceRuleTool,
                DeletePrincipleTool,
                DeleteSectionItemTool,
                DeleteSectionTool,
                UpdateMetaTool,
            ]

        return [
            ProceedToNextStepTool,
            GitGrepTool,
            UserSelectTool,
            ListFilesTool,
            AddFilesTool,
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        runnable = self.create_runnable(state)

        agent_state, config = await self.generate_agent_state(state, config)
        record_response_service = self.app.make(RecordResponseService)

        self.app.dispatch_task(
            record_response_service.record_response(agent_state, runnable, self.name, config),
        )
        result = await runnable.ainvoke(agent_state, config=config)

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": AIMessage(content=msg, agent_name=self.name)})
