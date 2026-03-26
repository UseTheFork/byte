from pathlib import Path
from typing import Literal, Type

from langchain_core.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState, EndNode, Node
from byte.lint import LintService
from byte.support import Str


class LintNode(Node):
    def boot(
        self,
        goto: Type[Node] = EndNode,
        **kwargs,
    ):
        self.goto = Str.class_to_snake_case(goto)

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:
        lint_service = self.app.make(LintService)

        if not self.app["config"].lint.enable:
            return Command(goto="routing_node", update={"node_to": self.goto})

        # Extract file paths from parsed blocks
        file_paths = []
        for block in state["parsed_blocks"]:
            if block.get("file_path"):
                file_paths.append(Path(str(block.get("file_path"))))

        lint_commands = await lint_service.lint_files(file_paths)

        do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
        if do_fix:
            joined_lint_errors = lint_service.format_lint_errors(failed_commands)
            return Command(
                goto="routing_node",
                update={"node_to": "coder_agent", "scratch_messages": HumanMessage(joined_lint_errors)},
            )

        return Command(goto="routing_node", update={"node_to": self.goto})
