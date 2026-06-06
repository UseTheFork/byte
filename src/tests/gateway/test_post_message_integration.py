"""Integration tests for GatewayService.post_message over real WebSocket."""

import asyncio
import json
from typing import TYPE_CHECKING, Any

import pytest
import pytest_asyncio
import websockets

from byte.gateway import GatewayService, GatewayServiceProvider
from byte.gateway.protocol import RpcRequest
from byte.tui import Status
from byte.tui.messages import Messages

if TYPE_CHECKING:
    from byte import Application
    from byte.config import ByteUserConfig


@pytest.fixture
def providers():
    """Provide GatewayServiceProvider for gateway integration tests."""
    return [GatewayServiceProvider]


@pytest_asyncio.fixture
async def gateway(application: Application) -> Any:
    """Start GatewayService with real WebSocket server for integration testing."""
    service = application.make(GatewayService)

    # Start the server in the background
    server_task = asyncio.create_task(service.start())

    # Wait briefly for the server to bind
    await asyncio.sleep(0.1)

    yield service

    # Cleanup: stop the service and cancel the task
    await service.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass


async def _connect_and_auth(gateway: GatewayService, config: ByteUserConfig) -> Any:
    """Open WebSocket, authenticate with token, and return the open connection."""
    ws = await websockets.connect(f"ws://{gateway._config.host}:{gateway._config.port}")

    # Send auth request
    auth_request = RpcRequest(jsonrpc="2.0", method="auth", params={"token": gateway._token}, id=1)
    await ws.send(auth_request.model_dump_json())

    # Consume OK response
    response_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
    response = json.loads(response_raw)
    assert response.get("result", {}).get("ok") is True

    return ws


@pytest.mark.asyncio
async def test_post_message_response_over_ws(gateway: GatewayService, config: ByteUserConfig) -> None:
    """Test post_message routes Response over real WebSocket."""
    ws = await _connect_and_auth(gateway, config)
    try:
        event = Messages.Response(chunk="hello", status=Status.SUCCESS)
        gateway.post_message(event)

        await asyncio.sleep(0.05)

        notification_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        notification = json.loads(notification_raw)

        assert notification["method"] == "stream/response"
        assert notification["params"]["content"] == "hello"
        assert notification["params"]["done"] is True
    finally:
        await ws.close()


@pytest.mark.asyncio
async def test_post_message_tool_response_over_ws(gateway: GatewayService, config: ByteUserConfig) -> None:
    """Test post_message routes ToolResponse over real WebSocket."""
    ws = await _connect_and_auth(gateway, config)
    try:
        event = Messages.ToolResponse(tool_name="search", chunk="results", tool_id="test")
        gateway.post_message(event)

        await asyncio.sleep(0.05)

        notification_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        notification = json.loads(notification_raw)

        assert notification["method"] == "stream/tool"
        assert notification["params"]["tool"] == "search"
        assert notification["params"]["content"] == "results"
    finally:
        await ws.close()


@pytest.mark.asyncio
async def test_post_message_command_completed_over_ws(gateway: GatewayService, config: ByteUserConfig) -> None:
    """Test post_message routes CommandExecutionCompleted over real WebSocket."""
    ws = await _connect_and_auth(gateway, config)
    try:
        event = Messages.CommandExecutionCompleted()
        gateway.post_message(event)

        await asyncio.sleep(0.05)

        notification_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        notification = json.loads(notification_raw)

        assert notification["method"] == "stream/done"
        assert notification["params"] == {}
    finally:
        await ws.close()


@pytest.mark.asyncio
async def test_post_message_error_status_over_ws(gateway: GatewayService, config: ByteUserConfig) -> None:
    """Test post_message routes error Status over real WebSocket."""
    ws = await _connect_and_auth(gateway, config)
    try:
        event = Messages.Status(state="error", message="something broke")
        gateway.post_message(event)

        await asyncio.sleep(0.05)

        notification_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        notification = json.loads(notification_raw)

        assert notification["method"] == "stream/error"
        assert notification["params"]["message"] == "something broke"
    finally:
        await ws.close()
