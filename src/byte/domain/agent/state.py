from typing import Annotated, TypedDict

from langgraph.graph.message import AnyMessage, add_messages

from byte.domain.edit_format.service.edit_format_service import SearchReplaceBlock


class BaseState(TypedDict):
	"""Base state that all agents inherit with messaging and status tracking.

	Usage: `state = BaseState(messages=[], agent="CoderAgent", agent_status="active", errors=[])`
	"""

	messages: Annotated[list[AnyMessage], add_messages]
	masked_messages: list[AnyMessage]

	agent: str

	agent_status: str
	errors: list[AnyMessage]


class CoderState(BaseState):
	"""Coder-specific state with file context."""

	edit_format_system: str

	parsed_blocks: list[SearchReplaceBlock]


class AskState(CoderState):
	"""State for ask/question agent with file context capabilities.

	Usage: `state = AskState(messages=[], agent="AskAgent", ...)`
	"""

	pass


class CommitState(BaseState):
	"""State for commit agent with generated commit message storage.

	Usage: `state = CommitState(messages=[], agent="CommitAgent", commit_message="")`
	"""

	commit_message: str


class CleanerState(BaseState):
	"""State for cleaner agent with content extraction fields.

	Extends BaseState with fields for content cleaning and information
	extraction, storing both raw input and cleaned output.
	Usage: `state = CleanerState(messages=[], cleaned_content="")`
	"""

	cleaned_content: str
