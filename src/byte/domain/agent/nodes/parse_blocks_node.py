from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.logging import log
from byte.core.utils import extract_content_from_message, get_last_message
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.edit_format.exceptions import PreFlightCheckError
from byte.domain.edit_format.schemas import BlockStatus
from byte.domain.edit_format.service.edit_format_service import (
	EditFormatService,
)


class ParseBlocksNode(Node):
	async def boot(self, edit_format: EditFormatService, **kwargs):
		self.edit_format = edit_format

	async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
		"""Parse commands from the last assistant message."""
		console = await self.make(ConsoleService)

		last_message = get_last_message(state["messages"])
		response_text = extract_content_from_message(last_message)

		try:
			parsed_blocks = await self.edit_format.handle(response_text)
		except Exception as e:
			if isinstance(e, PreFlightCheckError):
				console.print_warning_panel("Pre-flight check failed. Requesting corrections...", title="Parse Error")
				return Command(goto="assistant_node", update={"errors": [("user", str(e))]})

			log.exception(e)
			raise

		# Check for validation errors in parsed blocks
		validation_errors = []
		valid_count = 0

		for block in parsed_blocks:
			if block.block_status != BlockStatus.VALID:
				error_info = f"{block.status_message}\n\n{block.to_search_replace_format()}"
				validation_errors.append(error_info)
			else:
				valid_count += 1

		if validation_errors:
			failed_count = len(validation_errors)
			error_message = f"The following {failed_count} *SEARCH/REPLACE blocks* failed. Check the file content and try again. The other {valid_count} *SEARCH/REPLACE blocks* succeeded.\n\n"
			error_message += "\n\n".join(validation_errors)

			console.print_warning_panel(
				f"{failed_count} block(s) failed validation. Requesting corrections...", title="Validation Error"
			)

			return Command(goto="assistant_node", update={"errors": [("user", error_message)]})

		return Command(goto="lint_node", update={"parsed_blocks": parsed_blocks})
