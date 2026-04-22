from abc import abstractmethod
from datetime import datetime
from typing import List

from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from pydantic import Field

from byte.llm import ModelSchema
from byte.node import (
    BaseNode,
    NodeEvents,
)
from byte.orchestration import BaseState, PromptAssembler
from byte.support import Str


class BaseByteAIMessage(AIMessage):
    created_at: datetime = Field(default_factory=datetime.now)


class BaseAgentNode(BaseNode):
    @property
    def name(self) -> str:
        """Command name used for invocation (without prefix).

        Usage: return "add" for /add command
        """
        return Str.class_to_snake_case(self.__class__.__name__)

    def get_enforcement(self) -> List[str]:
        return []

    def get_tools(self):
        return []

    def get_structured_output(self):
        return None

    @abstractmethod
    def get_user_template(self) -> List[str]:
        """Get the user message template for this agent.

        Must be implemented by subclasses to return their specific user message
        template, which defines how user requests are formatted in prompts.
        Usage: Override in subclass to provide domain-specific user message formatting
        """
        pass

    @abstractmethod
    def get_prompt(self) -> ChatPromptTemplate:
        """Get the ChatPromptTemplate for this agent.

        Must be implemented by subclasses to return their specific ChatPromptTemplate,
        which defines the overall prompt structure including system and user messages.
        Usage: Override in subclass to provide domain-specific prompt templates
        """
        pass

    @abstractmethod
    def get_model(self) -> tuple[ModelSchema, dict]:
        """ """
        pass

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

    async def generate_agent_state(self, state: BaseState, config) -> tuple:
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
        prompt_assembler = self.app.make(PromptAssembler, template=self.get_user_template())

        model_schema, _ = self.get_model()
        user_prompt_state = await prompt_assembler.generate_state(state, self.__class__.__name__, model_schema)

        payload = await self.emit(
            NodeEvents.PreAssistantNode(
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

    def create_runnable(self, force_tool_choice: str | None = None) -> Runnable:
        """Create the runnable chain from context configuration.

        Assembles the prompt and model based on the mode (main or weak AI).
        If tools are provided, binds them to the model with parallel execution disabled.

        Args:
                context: The assistant context containing prompt, models, mode, and tools

        Returns:
                Runnable chain ready for invocation

        Usage: `runnable = self._create_runnable(model, runtime.context)`
        """

        model_schema, merged_params = self.get_model()
        model = init_chat_model(
            model_schema.model,
            model_provider=model_schema.provider,
            **merged_params,
        )

        if self.get_structured_output() is not None:
            model = model.with_structured_output(self.get_structured_output())

        # Bind tools if provided
        if self.get_tools() is not None and len(self.get_tools()) > 0:
            if force_tool_choice:
                model = model.bind_tools(self.get_tools(), tool_choice=force_tool_choice)
            else:
                model = model.bind_tools(self.get_tools())

        # Assemble the chain
        runnable = self.get_prompt() | model

        return runnable
