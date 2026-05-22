import asyncio
from abc import abstractmethod
from typing import TYPE_CHECKING, List, Sequence

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langgraph.types import Command

from byte.analytics import UsageMetrics
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseNode,
)
from byte.orchestration import (
    MessageFragment,
    MessageFragments,
    PhaseModel,
    PhaseUtils,
    PromptAssembler,
)
from byte.orchestration.messages import AIMessage
from byte.support import Str
from byte.tools import ToolRegistryService
from byte.tui import Messages

if TYPE_CHECKING:
    from byte.orchestration import BaseState


class BaseAgentNode(BaseNode):
    llm_tier: str = "standard"

    @property
    def name(self) -> str:
        """Agent Name"""
        return Str.class_to_snake_case(self.__class__.__name__)

    @property
    def human_name(self) -> str:
        """Human readable agent name"""
        return Str.snake_to_title(self.name).replace("Agent Node", "").strip()

    def get_tools(self, state: BaseState):
        return []

    def filter_message_history(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        return messages

    @abstractmethod
    def get_user_template(self) -> List[str]:
        """Get the user message template for this agent.

        Must be implemented by subclasses to return their specific user message
        template, which defines how user requests are formatted in prompts.
        Usage: Override in subclass to provide domain-specific user message formatting
        """
        ...

    @abstractmethod
    def get_system_template(self) -> List[str]:
        """ """
        ...

    @abstractmethod
    def get_context_template(self) -> List[str]:
        """ """
        ...

    def get_prompt(self, current_state: dict) -> List[MessageFragment]:
        return [
            MessageFragments.System(),
            MessageFragments.User(),
            MessageFragments.Scratch(),
            MessageFragments.Context(),
        ]

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.llm_tier)

    async def generate_prompt(self, prompt_assembler: PromptAssembler) -> List[BaseMessage]:
        message_fragments = self.get_prompt(prompt_assembler.get_assembled_state())

        # Run leaves concurrently (results preserve input order)
        results = await asyncio.gather(
            *(message_fragment.assemble(prompt_assembler) for message_fragment in message_fragments)
        )

        messages: List[BaseMessage] = []

        for result in results:
            if result is None:
                continue

            # MessageFragment returns a single message
            if isinstance(result, BaseMessage):
                messages.append(result)
                continue

            # MessageFragment returns multiple messages (e.g., scratch/history)
            if isinstance(result, Sequence) and not isinstance(result, (str, bytes)):
                for item in result:
                    if not isinstance(item, BaseMessage):
                        raise TypeError(
                            f"MessageFragment returned a sequence containing non-BaseMessage item: {type(item)}"
                        )
                    messages.append(item)
                continue

            raise TypeError(
                f"MessageFragment returned unsupported type: {type(result)}. Expected BaseMessage or Sequence[BaseMessage]."
            )

        return messages

    async def generate_agent_state(self, state: BaseState, config, extra: dict = {}) -> PromptAssembler:
        """Generate the agent state for the assistant node invocation.

        Assembles the user prompt from the state and context, emits a pre-assistant event
        for hooks to modify the state, and prepares the final agent state with assembled
        messages and any error context.

        Args:
            state: The current conversation state
            config: The runnable configuration
            context: The assistant context containing templates and configuration

        Returns:
            Tuple of (agent_state dict, updated config)

        Usage: `agent_state, config = await self._generate_agent_state(state, config, runtime.context)`
        """

        # Create a new assembler
        prompt_assembler = self.app.make(PromptAssembler, agent_node=self, state=state, extra=extra)

        agent_state = await prompt_assembler.generate_messages()

        # TODO: DO we need this?
        agent_state["errors"] = []

        scratch_messages = state.get("scratch_messages", [])
        _, memory_percent = UsageMetrics.estimate_prompt_tokens(agent_state, scratch_messages)

        self.app.emit_tui(
            Messages.UpdateMemory(
                memory_percent=memory_percent,
            )
        )

        # TODO: make this better
        return prompt_assembler

    def create_runnable(
        self, prompt_assembler: PromptAssembler, tool_choice: dict[str, str] | str | None = None
    ) -> Runnable:
        model_schema, merged_params = self.get_model()
        model = init_chat_model(
            model_schema.model,
            model_provider=model_schema.provider,
            **merged_params,
        )

        tool_schemas = []
        tool_registry_service = self.app.make(ToolRegistryService)

        is_workflow_agent = PhaseUtils.is_workflow_agent(prompt_assembler.get_state())
        # Find the first pending step (if any)
        pending_phase = PhaseUtils.get_pending_phase(prompt_assembler.get_state())

        if pending_phase is not None and isinstance(pending_phase, PhaseModel):
            # Append any step-specific tools
            if pending_phase.tools:
                for tool_class in pending_phase.tools:
                    tool = tool_registry_service.get_tool(tool_class.name)
                    assert tool
                    tool_schema = PhaseUtils.inject_phase_input_schema_args(tool.tool_schema())
                    tool_schemas.append(tool_schema)

        # Bind agent-level tools if provided
        agent_tools = self.get_tools(prompt_assembler.get_state())
        if agent_tools:
            for tool in agent_tools:
                tool_schema = tool.tool_schema()
                if is_workflow_agent:
                    tool_schema = PhaseUtils.inject_phase_input_schema_args(tool.tool_schema())
                tool_schemas.append(tool_schema)

        self.app["log"].info(tool_schemas)

        # Bind tool schemas to the model
        if tool_choice:
            model = model.bind_tools(tool_schemas, tool_choice=tool_choice)
        else:
            model = model.bind_tools(tool_schemas)

        return model

    def route_tool_calls(self, result) -> Command | None:
        """Route to the tool node when the model returns tool calls.

        Casts the result to this agent's message type and routes to the tool node
        with the result appended to scratch_messages.

        Args:
            result: The raw model result containing tool calls

        Returns:
            Command routing to "tool_node" with the cast result in scratch_messages
        """
        if result.tool_calls and len(result.tool_calls) > 0:
            result = AIMessage.from_langchain(result, agent_name=self.name)
            return self.route_to(
                "tool_node",
                {
                    "scratch_messages": [result],
                    "errors": None,
                },
            )

        return None
