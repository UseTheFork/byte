from pathlib import Path
from textwrap import dedent

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.state import CoderState
from byte.domain.lint.service.lint_service import LintService


class LintNode(Node):
	async def __call__(self, state: CoderState, config: RunnableConfig):
		lint_service = await self.make(LintService)

		# Extract file paths from parsed blocks
		file_paths = [Path(block.file_path) for block in state["parsed_blocks"]]

		lint_commands = await lint_service.lint_files(file_paths)

		do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
		if do_fix:
			lint_errors = []
			for lint_file in failed_commands:
				error_msg = lint_file.stderr.strip() or lint_file.stdout.strip()
				lint_error_message = dedent(f"""
					<lint_error: source={lint_file.file}>
					{error_msg}
					</lint_error>""")
				lint_errors.append(lint_error_message)

			joined_lint_errors = "**Fix The Following Lint Errors**\n\n" + "\n\n".join(lint_errors)

			return Command(goto="assistant_node", update={"errors": [("user", joined_lint_errors)]})

		return Command(goto="end_node")
