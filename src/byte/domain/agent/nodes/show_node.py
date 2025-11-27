from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService


class ShowNode(AssistantNode):
    """Node for extracting and copying code blocks to clipboard.

    Parses code blocks from the last message, displays truncated previews,
    and allows user to select which block to copy to clipboard.
    Usage: Used in CopyAgent workflow via `/copy` command
    """

    async def __call__(self, state: BaseState, config, runtime: Runtime[AssistantContextSchema]):
        """Extract code blocks and prompt user to select one for clipboard copy."""
        agent_state, config = await self._generate_agent_state(state, config, runtime)

        runnable = self._create_runnable(runtime.context)

        template = runnable.get_prompts(config)
        prompt_value = await template[0].ainvoke(agent_state)

        console = await self.make(ConsoleService)

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

        return Command(goto="end_node", update=state)
