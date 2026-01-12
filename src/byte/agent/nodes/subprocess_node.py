from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState, Node
from byte.cli import SubprocessService
from byte.prompt_format import Boundary, BoundaryType
from byte.support.mixins import UserInteractive
from byte.support.utils import list_to_multiline_text


class SubprocessNode(Node, UserInteractive):
    """Node for executing subprocess commands and optionally adding results to conversation.

    Executes shell commands via SubprocessService, displays the results to the user,
    and prompts whether to include the output in the conversation context for AI awareness.
    Usage: Used in SubprocessAgent workflow via `!command` syntax
    """

    async def _display_subprocess_results(self, subprocess_result):
        """Display subprocess execution results and prompt user to add to messages.

        Shows the command output in a panel and asks if the user wants to include
        the results in the conversation context for AI awareness.

        Usage: `await self._display_subprocess_results(result)` -> displays and prompts
        """
        console = self.app["console"]

        # Display the results with more detail
        result_display = f"Exit Code: {subprocess_result.exit_code}\n\nOutput:\n{subprocess_result.stdout}"
        if subprocess_result.stderr:
            result_display += f"\n\nErrors:\n{subprocess_result.stderr}"

        console.print_panel(result_display, title=f"Command: {subprocess_result.command}")

        # Ask user if they want to add results to messages
        should_add = await self.prompt_for_confirmation("Add subprocess output to conversation context?", default=True)

        return should_add

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["end_node"]]:
        """Execute subprocess command and optionally add results to messages.

        Args:
                state: SubprocessState containing the command to execute
                config: LangGraph runnable configuration

        Returns:
                Command with optional message update if user confirms adding results

        Usage: Called automatically by SubprocessAgent during graph execution
        """

        subprocess_command = state["user_request"]
        subprocess_service = self.app.make(SubprocessService)
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
