from pathlib import Path
from typing import Literal, Type

from langchain_core.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.lint import LintService
from byte.node import BaseNode
from byte.node.nodes import EndNode
from byte.orchestration import BaseState
from byte.support import Str


class LintNode(BaseNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        self.goto = Str.class_to_snake_case(goto)

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:
        lint_service = self.app.make(LintService)

        if not self.app["config"].lint.enable:
            return self.route_to(self.goto)

        # Extract file paths from parsed blocks
        file_paths = []
        for path in state["touched_files"]:
            file_paths.append(Path(str(path)))

        lint_commands = await lint_service.lint_files(file_paths)

        do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
        if do_fix:
            joined_lint_errors = lint_service.format_lint_errors(failed_commands)
            return self.route_to("coder_agent", {"scratch_messages": HumanMessage(joined_lint_errors)})

        return self.route_back(state)
