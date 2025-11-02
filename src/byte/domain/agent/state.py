from typing import Annotated, TypedDict

from langgraph.graph.message import AnyMessage, add_messages

from byte.domain.agent.reducers import add_constraints
from byte.domain.agent.schemas import ConstraintSchema
from byte.domain.edit_format.service.edit_format_service import SearchReplaceBlock


class BaseState(TypedDict):
	"""Base state that all agents inherit with messaging and status tracking.

	Usage: `state = BaseState(messages=[], agent="CoderAgent", errors=[])`
	"""

	messages: Annotated[list[AnyMessage], add_messages]
	constraints: Annotated[list[ConstraintSchema], add_constraints]
	masked_messages: list[AnyMessage]

	agent: str

	errors: str | None
	examples: list[AnyMessage]

	extracted_content: str


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


class SubprocessState(BaseState):
	""" """

	command: str
