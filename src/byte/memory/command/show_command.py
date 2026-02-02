from argparse import Namespace
from typing import cast

from langchain_core.runnables import RunnableConfig

from byte.agent import Agent, AgentServiceProvider, AssistantNode, BaseState
from byte.cli import ByteArgumentParser, Command, InputCancelledError
from byte.memory import MemoryService
from byte.support import Str
from byte.support.mixins import UserInteractive


class ShowCommand(Command, UserInteractive):
    """Command to display the current conversation history and context.

    Invokes the ShowAgent to render the conversation state, including
    messages, file context, and other relevant information without
    making any modifications or AI calls.
    Usage: `/show` -> displays current conversation state
    """

    @property
    def name(self) -> str:
        return "show"

    @property
    def category(self) -> str:
        return "Memory"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Display the current conversation history and context",
        )
        return parser

    def boot(self, *args, **kwargs) -> None:
        agent_service_provider = self.app.make(AgentServiceProvider)

        # Get all available agents and convert to string names
        self.agent_names = {Str.class_to_name(agent): agent for agent in agent_service_provider.agents()}

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the Show agent to display conversation state.

        Invokes the ShowAgent through the agent service to render the current
        conversation history and context without making any modifications.

        Args:
            args: Unused for this command (empty string expected)

        Usage: Called automatically when user types `/show`
        """

        console = self.app["console"]

        # Prompt user to select an agent
        try:
            agent_name = await self.prompt_for_select_numbered(
                "Select an agent to show conversation state:", list(self.agent_names.keys()), default=0
            )
        except InputCancelledError:
            return

        # Validate that the agent exists
        if agent_name not in self.agent_names:
            console.print_error(
                f"Agent '{agent_name}' not found. Available agents: {', '.join(self.agent_names.keys())}"
            )
            return

        agent_class = self.agent_names[agent_name]
        agent: Agent = self.app.make(agent_class)
        compiled_graph = await agent.get_graph()

        memory_service = self.app.make(MemoryService)
        thread_id = await memory_service.get_or_create_thread()
        config = RunnableConfig(configurable={"thread_id": thread_id})

        last_state = await compiled_graph.aget_state(config)

        assistant_node = self.app.make(AssistantNode)
        context = await agent.get_assistant_runnable()
        agent_state, config = await assistant_node._generate_agent_state(
            cast(BaseState, last_state.values),
            last_state.config,
            context,
        )

        runnable = assistant_node._create_runnable(context)

        template = runnable.get_prompts(config)
        prompt_value = await template[0].ainvoke(agent_state)
        messages = prompt_value.to_messages()

        for message in messages:
            message_type = type(message).__name__

            # Determine border style based on message type
            border_style = "primary"
            if message_type == "SystemMessage":
                border_style = "danger"
            elif message_type == "HumanMessage":
                border_style = "info"
            elif message_type == "AIMessage":
                border_style = "secondary"

            console.panel_top(f"Message: {message_type}", border_style=border_style)
            console.print("")
            console.print(message.content)
            console.print("")
            console.panel_bottom(border_style=border_style)
