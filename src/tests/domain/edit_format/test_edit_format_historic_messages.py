"""Test suite for EditFormatService historic message handling.

Tests the replace_blocks_in_historic_messages_hook method that processes
AIMessage history to remove SEARCH/REPLACE blocks from older messages.
"""

import dill
import pytest

from byte.core.config.config import PROJECT_ROOT
from byte.core.event_bus import EventType, Payload
from byte.core.utils import dump


class TestEditFormatHistoricMessages:
	"""Test suite for historic message processing."""

	@pytest.fixture
	def seven_messages_fixture(self) -> dict:
		"""Load the seven_messages.json fixture data.

		Returns:
			dict: Parsed JSON fixture data containing state with messages
		"""
		fixture_path = PROJECT_ROOT / "src" / "tests" / "fixtures" / "agent" / "coder" / "multiple_edits_and_error.pkl"
		with open(fixture_path, "rb") as fp:
			return dill.load(fp)

	@pytest.mark.asyncio
	async def test_load_seven_messages_fixture(self, seven_messages_fixture: dict):
		"""Verify the fixture loads correctly and contains expected structure."""

		assert "messages" in seven_messages_fixture
		messages = seven_messages_fixture["messages"]
		assert len(messages) == 12

	@pytest.mark.asyncio
	async def test_replace_blocks_in_historic_messages_hook(
		self,
		edit_format_service,
		seven_messages_fixture: dict,
	):
		"""Test that SEARCH/REPLACE blocks are removed from historic AIMessages.

		Verifies that:
		- Only AIMessages are processed
		- The last 2 AIMessages are preserved unchanged
		- Earlier AIMessages have their SEARCH/REPLACE blocks removed
		- Blocks are replaced with summary messages
		- Non-AIMessages remain unchanged
		"""
		payload = Payload(
			event_type=EventType.PRE_ASSISTANT_NODE,
			data={
				"state": seven_messages_fixture,
				"config": {},
			},
		)

		# Get original messages for comparison
		original_messages = payload.get("state")["messages"]

		# Count AIMessages and identify which ones should be processed
		from langchain_core.messages import AIMessage

		ai_message_indices = [i for i, msg in enumerate(original_messages) if isinstance(msg, AIMessage)]

		# Store original content of messages that should be modified
		messages_to_modify = ai_message_indices[:-2] if len(ai_message_indices) > 2 else []

		# Store original content of last 2 AIMessages (should not change)
		last_two_indices = ai_message_indices[-2:] if len(ai_message_indices) > 2 else ai_message_indices
		last_two_original_content = {idx: str(original_messages[idx].content) for idx in last_two_indices}

		# Execute the hook
		result_payload = await edit_format_service.replace_blocks_in_historic_messages_hook(payload)

		# Get modified messages
		modified_messages = result_payload.get("state")["messages"]

		# Verify message count hasn't changed
		assert len(modified_messages) == len(original_messages)

		# Verify last 2 AIMessages are unchanged
		for idx in last_two_indices:
			assert str(modified_messages[idx].content) == last_two_original_content[idx], (
				f"Last 2 AIMessages should not be modified (index {idx})"
			)

		# Verify earlier AIMessages have blocks removed
		for idx in messages_to_modify:
			modified_content = str(modified_messages[idx].content)

			dump(modified_content)

			# Should not contain SEARCH/REPLACE markers
			assert "<<<<<<< SEARCH" not in modified_content, (
				f"Historic message {idx} should have SEARCH markers removed"
			)
			assert ">>>>>>> REPLACE" not in modified_content, (
				f"Historic message {idx} should have REPLACE markers removed"
			)
			assert "=======" not in modified_content or "Changes applied" in modified_content, (
				f"Historic message {idx} should have blocks replaced with summary"
			)

			# Should contain summary messages for blocks that were present
			original_content = str(original_messages[idx].content)
			if "<<<<<<< SEARCH" in original_content:
				assert "Changes applied" in modified_content, (
					f"Historic message {idx} should have summary for removed blocks"
				)

		# Verify non-AIMessages remain unchanged
		for idx, msg in enumerate(original_messages):
			if not isinstance(msg, AIMessage):
				assert modified_messages[idx].content == msg.content, (
					f"Non-AIMessage at index {idx} should remain unchanged"
				)
