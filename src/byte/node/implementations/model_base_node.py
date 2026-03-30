from typing import Type

from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from byte import Events
from byte.node import EndNode, Node
from byte.orchestration import AssistantContextSchema, BaseState, PromptAssembler
from byte.support import Str


class ModelBaseNode(Node):
    def boot(
        self,
        goto: Type[Node] = EndNode,
        structured_output: BaseModel | None = None,
        **kwargs,
    ):
        self.structured_output = structured_output
        self.goto = Str.class_to_snake_case(goto)

    def _create_runnable(self, model: BaseChatModel, context: AssistantContextSchema) -> Runnable:
        """Create the runnable chain from context configuration.

        Assembles the prompt and model based on the mode (main or weak AI).
        If tools are provided, binds them to the model with parallel execution disabled.

        Args:
                context: The assistant context containing prompt, models, mode, and tools

        Returns:
                Runnable chain ready for invocation

        Usage: `runnable = self._create_runnable(model, runtime.context)`
        """
        # Bind Structred output if provided.
        if self.structured_output is not None:
            model = model.with_structured_output(self.structured_output)  # ty:ignore[invalid-argument-type]

        # Bind tools if provided
        if context.tools is not None and len(context.tools) > 0:
            model = model.bind_tools(context.tools)  # ty:ignore[unresolved-attribute]

        # Assemble the chain
        runnable = context.prompt | model  # ty:ignore[unsupported-operator]

        return runnable

    # TODO: Is this the right place for this?
    # This should prob go in to the prompt
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

        payload = await self.emit(
            Events.PreAssistantNode(
                state=user_prompt_state,
                config=config,
            )
        )
        user_prompt_state = payload.state

        agent_state = {**state}

        agent_state["assembled_user_message"] = prompt_assembler.assemble(**user_prompt_state)

        if state.get("errors", None) is not None:
            agent_state["errors"] = await self._gather_errors(agent_state)
        else:
            agent_state["errors"] = []

        config = payload.config

        return (agent_state, config)
