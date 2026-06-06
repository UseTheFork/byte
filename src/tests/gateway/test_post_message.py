"""Test suite for GatewayService.post_message."""

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from byte.gateway import GatewayService, GatewayServiceProvider
from byte.tui import Status
from byte.tui.messages import Messages

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide GatewayServiceProvider for gateway tests."""
    return [GatewayServiceProvider]


@pytest.fixture
def gateway(application: Application):
    """Create a GatewayService with mocked session for testing."""
    service = application.make(GatewayService)
    service._session = MagicMock()
    service._session.notify = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_post_message_response(gateway: GatewayService):
    """Test post_message routes Response messages to stream/response."""
    event = Messages.Response(chunk="hello", status=Status.SUCCESS)

    with patch("asyncio.create_task") as mock_create_task:
        gateway.post_message(event)

        mock_create_task.assert_called_once()
        coroutine = mock_create_task.call_args[0][0]
        await coroutine

        gateway._session.notify.assert_called_once_with("stream/response", {"content": "hello", "done": True})  # ty:ignore[unresolved-attribute]


@pytest.mark.asyncio
async def test_post_message_tool_response(gateway: GatewayService):
    """Test post_message routes ToolResponse messages to stream/tool."""
    event = Messages.ToolResponse(tool_name="search", chunk="results", tool_id="test")

    with patch("asyncio.create_task") as mock_create_task:
        gateway.post_message(event)

        mock_create_task.assert_called_once()
        coroutine = mock_create_task.call_args[0][0]
        await coroutine

        gateway._session.notify.assert_called_once_with("stream/tool", {"tool": "search", "content": "results"})  # ty:ignore[unresolved-attribute]


@pytest.mark.asyncio
async def test_post_message_command_completed(gateway: GatewayService):
    """Test post_message routes CommandExecutionCompleted to stream/done."""
    event = Messages.CommandExecutionCompleted()

    with patch("asyncio.create_task") as mock_create_task:
        gateway.post_message(event)

        mock_create_task.assert_called_once()
        coroutine = mock_create_task.call_args[0][0]
        await coroutine

        gateway._session.notify.assert_called_once_with("stream/done", {})  # ty:ignore[unresolved-attribute]


@pytest.mark.asyncio
async def test_post_message_error_status(gateway: GatewayService):
    """Test post_message routes error Status messages to stream/error."""
    event = Messages.Status(state="error", message="something broke")

    with patch("asyncio.create_task") as mock_create_task:
        gateway.post_message(event)

        mock_create_task.assert_called_once()
        coroutine = mock_create_task.call_args[0][0]
        await coroutine

        gateway._session.notify.assert_called_once_with("stream/error", {"message": "something broke"})  # ty:ignore[unresolved-attribute]


@pytest.mark.asyncio
async def test_post_message_no_session_returns_early(gateway: GatewayService):
    """Test post_message returns early when _session is None."""
    gateway._session = None
    event = Messages.Response(chunk="hello", status=Status.SUCCESS)

    with patch("asyncio.create_task") as mock_create_task:
        gateway.post_message(event)

        mock_create_task.assert_not_called()


@pytest.mark.asyncio
async def test_post_message_unmatched_event_ignored(gateway: GatewayService):
    """Test post_message ignores unmatched message types."""
    from textual.message import Message

    event = Message()

    with patch("asyncio.create_task") as mock_create_task:
        gateway.post_message(event)

        mock_create_task.assert_not_called()
