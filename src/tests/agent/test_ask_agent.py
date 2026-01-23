"""Test suite for Ask Agent."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from langchain.messages import AIMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

from byte.llm import LLMService

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide AgentServiceProvider for ask agent tests."""
    from byte.agent import AgentServiceProvider

    return [AgentServiceProvider]


@pytest.mark.asyncio
async def test_ask_agent_responds_to_query(application: Application, mocker):
    """Test that Ask Agent responds to a basic query."""

    patched_model = GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(content="hello world"),
            ]
        )
    )

    mocker.patch.object(LLMService, "get_main_model", return_value=patched_model)

    from byte.agent.implementations.ask.agent import AskAgent

    # Create the agent
    agent = application.make(AskAgent)

    result = await agent.execute("What is Python?", display_mode="silent")

    # Verify the agent responded with a message
    assert "history_messages" in result
    assert len(result["history_messages"]) == 2  # User message + AI response
    assert result["history_messages"][0].content == "What is Python?"
    assert result["history_messages"][1].content == "hello world"
    assert len(result["history_messages"][1].content) > 0
