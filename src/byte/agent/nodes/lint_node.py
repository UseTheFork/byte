from pathlib import Path
from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState, Node
from byte.lint import LintService


class LintNode(Node):
    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["end_node", "assistant_node"]]:
        lint_service = self.app.make(LintService)

        if not self.app["config"].lint.enable:
            return Command(goto="end_node")

        # Extract file paths from parsed blocks
        file_paths = [Path(block.file_path) for block in state["parsed_blocks"]]

        lint_commands = await lint_service.lint_files(file_paths)

        do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
        if do_fix:
            joined_lint_errors = lint_service.format_lint_errors(failed_commands)
            return Command(goto="assistant_node", update={"scratch_messages": HumanMessage(joined_lint_errors)})

        return Command(goto="end_node")
