from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import list_to_multiline_text
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.cli.service.subprocess_service import SubprocessService
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary


class SubprocessNode(Node, UserInteractive):
    """Node for executing subprocess commands and optionally adding results to conversation.

    Executes shell commands via SubprocessService, displays the results to the user,
    and prompts whether to include the output in the conversation context for AI awareness.
    Usage: Used in SubprocessAgent workflow via `!command` syntax
    """

    async def __call__(self, state: BaseState, config: RunnableConfig):
        """Execute subprocess command and optionally add results to messages.

        Args:
                state: SubprocessState containing the command to execute
                config: LangGraph runnable configuration

        Returns:
                Command with optional message update if user confirms adding results

        Usage: Called automatically by SubprocessAgent during graph execution
        """

        subprocess_command = state["command"]
        subprocess_service = await self.make(SubprocessService)
        subprocess_result = await subprocess_service.run(subprocess_command)

        should_add = await self._display_subprocess_results(subprocess_result)

        if should_add:
            # Format the result using XML-like syntax
            result_message = [
                Boundary.open(BoundaryType.CONTEXT, meta={"type": "subprocess execution"}),
                f"<command>{subprocess_result.command}</command>",
                f"<exit_code>{subprocess_result.exit_code}</exit_code><stdout>{subprocess_result.stdout}</stdout>",
            ]

            if subprocess_result.stderr:
                result_message.append("<stderr>{subprocess_result.stderr}</stderr>")
            result_message.append(
                Boundary.close(BoundaryType.CONTEXT),
            )

            return Command(
                goto="end_node", update={"scratch_messages": [("user", list_to_multiline_text(result_message))]}
            )

        return Command(goto="end_node")

    async def _display_subprocess_results(self, subprocess_result):
        """Display subprocess execution results and prompt user to add to messages.

        Shows the command output in a panel and asks if the user wants to include
        the results in the conversation context for AI awareness.

        Usage: `await self._display_subprocess_results(result)` -> displays and prompts
        """
        console = await self.make(ConsoleService)

        # Display the results with more detail
        result_display = f"Exit Code: {subprocess_result.exit_code}\n\nOutput:\n{subprocess_result.stdout}"
        if subprocess_result.stderr:
            result_display += f"\n\nErrors:\n{subprocess_result.stderr}"

        console.print_panel(result_display, title=f"Command: {subprocess_result.command}")

        # Ask user if they want to add results to messages
        should_add = await self.prompt_for_confirmation("Add subprocess output to conversation context?", default=True)

        return should_add
