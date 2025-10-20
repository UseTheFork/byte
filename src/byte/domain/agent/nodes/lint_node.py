from pathlib import Path

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

		await lint_service.lint_files(file_paths)

		return Command(goto="end_node")
