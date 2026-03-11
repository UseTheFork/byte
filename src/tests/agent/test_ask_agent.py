"""Test suite for Ask Agent."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide AgentServiceProvider for ask agent tests."""
    from byte.agent import AgentServiceProvider
    from byte.conventions import ConventionsServiceProvider
    from byte.git import GitServiceProvider

    return [AgentServiceProvider, ConventionsServiceProvider, GitServiceProvider]


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_ask_agent_responds_to_query(application: Application, mocker):
    """Test that Ask Agent responds to a basic query."""

    from byte.agent.implementations.ask.agent import AskAgent

    # Create the agent
    agent = application.make(AskAgent)

    result = await agent.execute("What is Python?", display_mode="silent")

    # Verify the agent responded with a message
    assert "history_messages" in result
    assert len(result["history_messages"]) == 2  # User message + AI response

    assert "<user_message>" in result["history_messages"][0].content
    assert "What is Python?" in result["history_messages"][0].content

    assert "'d be happy to explain what Python is!" in result["history_messages"][1].content
    assert '<agent_message agent_type="AskAgent">' in result["history_messages"][1].content
    assert "[{'text': " not in result["history_messages"][1].content

    assert len(result["history_messages"][1].content) > 0
