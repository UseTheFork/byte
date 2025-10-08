"""Test suite for EditFormatService historic message handling.

Tests the replace_blocks_in_historic_messages_hook method that processes
AIMessage history to remove SEARCH/REPLACE blocks from older messages.
"""

import dill
import pytest

from byte.core.config.config import PROJECT_ROOT
from byte.core.utils import dd


class TestEditFormatHistoricMessages:
    """Test suite for historic message processing."""

    @pytest.fixture
    def seven_messages_fixture(self) -> dict:
        """Load the seven_messages.json fixture data.

        Returns:
            dict: Parsed JSON fixture data containing state with messages
        """
        fixture_path = (
            PROJECT_ROOT
            / "src"
            / "tests"
            / "fixtures"
            / "agent"
            / "coder"
            / "recording_20251008_185105.pkl"
        )
        with open(fixture_path, "rb") as fp:
            return dill.load(fp)

    @pytest.mark.asyncio
    async def test_load_seven_messages_fixture(self, seven_messages_fixture: dict):
        """Verify the fixture loads correctly and contains expected structure."""

        dd(seven_messages_fixture)

        assert "state" in seven_messages_fixture
        assert "messages" in seven_messages_fixture["state"]
        messages = seven_messages_fixture["state"]["messages"]
        assert len(messages) == 7

    # @pytest.mark.asyncio
    # async def test_fixture_contains_ai_messages(self, seven_messages_fixture: dict):
    #     """Verify the fixture contains AIMessage objects."""
    #     messages = seven_messages_fixture["state"]["messages"]
    #     ai_messages = [msg for msg in messages if msg.get("type") == "ai"]
    #     assert len(ai_messages) > 0
