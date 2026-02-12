from typing import Literal, Type

from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import BaseModel

from byte import EventType, Payload
from byte.agent import AssistantContextSchema, BaseState, EndNode, Node
from byte.agent.utils.prompt_assembler import PromptAssembler
from byte.development import RecordResponseService
from byte.support import Str
from byte.support.utils import dd


class AssistantNode(Node):
    def boot(
        self,
        goto: Type[Node] = EndNode,
        structured_output: BaseModel | None = None,
        **kwargs,
    ):
        self.structured_output = structured_output
        self.goto = Str.class_to_snake_case(goto)

    def _create_runnable(self, context: AssistantContextSchema) -> Runnable:
        """Create the runnable chain from context configuration.

        Assembles the prompt and model based on the mode (main or weak AI).
        If tools are provided, binds them to the model with parallel execution disabled.

        Args:
                context: The assistant context containing prompt, models, mode, and tools

        Returns:
                Runnable chain ready for invocation

        Usage: `runnable = self._create_runnable(runtime.context)`
        """
        # Select model based on mode
        model = context.main if context.mode == "main" else context.weak

        # Bind Structred output if provided.
        if self.structured_output is not None:
            model = model.with_structured_output(self.structured_output)  # ty:ignore[invalid-argument-type, possibly-missing-attribute]

        # Bind tools if provided
        if context.tools is not None and len(context.tools) > 0:
            model = model.bind_tools(context.tools, parallel_tool_calls=False)  # ty:ignore[unresolved-attribute]

        # Assemble the chain
        runnable = context.prompt | model  # ty:ignore[unsupported-operator]

        return runnable

    async def _gather_errors(self, state) -> list[HumanMessage]:
        """Gather error messages from state for re-prompting the assistant.

        Formats validation or other errors into a user message that will
        be added to the conversation to guide the assistant's correction.

        Args:
                state: The current state containing errors

        Returns:
                List containing a single HumanMessage with error content, or empty list

        Usage: `error_messages = await self._gather_errors(state)`
        """
        errors = state.get("errors", None)

        if errors is None:
            return []

        return [HumanMessage(errors)]

    async def _generate_agent_state(self, state: BaseState, config, context: AssistantContextSchema) -> tuple:
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
        prompt_assembler = self.app.make(PromptAssembler, template=context.user_template)
        user_prompt_state = await prompt_assembler.generate_state(state, config, context)

        payload = Payload(
            event_type=EventType.PRE_ASSISTANT_NODE,
            data={
                "state": user_prompt_state,
                "config": config,
            },
        )

        payload = await self.emit(payload)
        user_prompt_state = payload.get("state", user_prompt_state)

        agent_state = {**state}

        agent_state["assembled_user_message"] = prompt_assembler.assemble(**user_prompt_state)

        if state.get("errors", None) is not None:
            agent_state["errors"] = await self._gather_errors(agent_state)
        else:
            agent_state["errors"] = []

        config = payload.get("config", config)

        return (agent_state, config)

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["end_node", "parse_blocks_node", "tool_node", "validation_node"]]:
        record_response_service = self.app.make(RecordResponseService)
        while True:
            agent_state, config = await self._generate_agent_state(state, config, runtime.context)

            runnable = self._create_runnable(runtime.context)

            with get_usage_metadata_callback() as usage_metadata_callback:
                result = await runnable.ainvoke(agent_state, config=config)
                await self._track_token_usage(usage_metadata_callback.usage_metadata, runtime.context.mode)
                await record_response_service.record_response(agent_state, runnable, runtime, config)

            # If we are requesting Structured output we can end with extracted being our structured output.
            if self.structured_output is not None:
                return Command(
                    goto="validation_node",
                    update={
                        "extracted_content": result,
                        "errors": None,
                    },
                )

            # Ensure we get a real response
            if not result.tool_calls and (
                not result.content
                or (
                    isinstance(result.content, list)
                    and len(result.content) > 0
                    and isinstance(result.content[0], dict)
                    and not result.content[0].get("text")
                )
            ):
                dd(result)
                # Re-prompt for actual response
                messages = agent_state["scratch_messages"] + [("user", "Respond with a real output.")]
                agent_state = {**agent_state, "scratch_messages": messages}
                console = self.app["console"]
                console.print_warning_panel(
                    "AI did not provide proper output. Requesting a valid response.", title="Warning"
                )

            elif result.tool_calls and len(result.tool_calls) > 0:
                return Command(
                    goto="tool_node",
                    update={
                        "scratch_messages": [result],
                        "errors": None,
                    },
                )
            else:
                break

        return Command(
            goto=str(self.goto),
            update={
                "scratch_messages": [result],
                "errors": None,
            },
        )
