from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AIMessage, BaseState, Leaves
from byte.support import Section, SectionType, Str
from byte.support.utils import extract_content_from_message


class AskAgentNode(BaseAgentNode):
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
            Leaves.Preamble(role="Act as an expert software developer."),
            Leaves.CommunicationStyle(verbose=True),
            Leaves.WorkflowConstraints(
                [
                    "- Always use best practices when coding",
                    "- Respect and use existing conventions, libraries, etc that are already present in the code base",
                    "- Take requests for changes to the supplied code",
                    "- If the request is ambiguous, ask questions",
                    "- Keep changes simple don't build more then what is asked for",
                    "- Do not provide full code implementations unless explicitly requested. Describe the changes needed first.",
                ]
            ),
            "",
            Section.start(SectionType.RESPONSE_FORMAT),
            "- Use clear, concise explanations",
            "- Format code with proper syntax highlighting",
            "- Provide context for suggested changes",
            "- Focus on actionable findings, not exhaustive documentation",
            Section.end(),
            "",
            Leaves.OperatingPrinciples(),
        ]

    def get_context_template(self):
        return [
            Leaves.ReferenceMaterials(),
            Leaves.ProjectEnvironment(),
            Leaves.FileContext(),
            Leaves.Epilogue(
                enforcements=[
                    "- NEVER use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
                    "- DO NOT provide full code implementations unless explicitly requested. Describe the changes needed first.",
                ]
            ),
        ]

    def get_tools(self, state: BaseState):
        return [
            # GitGrepTool,
            # UserSelectTool,
            # ListFilesTool,
            # AddFilesTool,
            # SearchWebTool,
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

        record_response_service = self.app.make(RecordResponseService)

        self.app.dispatch_task(
            record_response_service.record_response(prompt, config),
        )
        result = await runnable.ainvoke(
            prompt,
            config=config,
            cache_control={"type": "ephemeral"},
        )

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": AIMessage(content=msg, agent_name=self.human_name)})
