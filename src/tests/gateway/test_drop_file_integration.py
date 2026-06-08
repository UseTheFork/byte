"""Integration tests for Requests.DropFile over real WebSocket."""

import asyncio
import json
from typing import TYPE_CHECKING, Any

import pytest
import pytest_asyncio
import websockets

from byte.gateway import GatewayService
from byte.gateway.protocol import RpcRequest

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide GatewayServiceProvider for gateway integration tests."""
    from byte.files import FileServiceProvider
    from byte.gateway import GatewayServiceProvider

    return [GatewayServiceProvider, FileServiceProvider]


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


async def _connect_and_auth(gateway: GatewayService, config: Any) -> Any:
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
async def test_drop_file_success_over_ws(gateway: GatewayService, config: Any) -> None:
    """Test drop_file request returns success response over real WebSocket."""
    ws = await _connect_and_auth(gateway, config)
    try:
        # Send add_file request
        add_file_request = RpcRequest(
            jsonrpc="2.0",
            method="add_file",
            params={"file_path": "README.md"},
            id=2,
        )
        await ws.send(add_file_request.model_dump_json())

        # Receive response
        response_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)

        # Send drop_file request
        drop_file_request = RpcRequest(
            jsonrpc="2.0",
            method="drop_file",
            params={"file_path": "README.md"},
            id=2,
        )
        await ws.send(drop_file_request.model_dump_json())

        # Receive response
        response_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        response = json.loads(response_raw)

        assert response["id"] == 2
        assert response.get("result", {}).get("ok") is True
        assert response.get("result", {}).get("file_path") == "README.md"
        assert response.get("error") is None
    finally:
        await ws.close()


@pytest.mark.asyncio
async def test_drop_file_not_in_context_over_ws(gateway: GatewayService, config: Any) -> None:
    """Test drop_file request returns error when file not in context."""
    ws = await _connect_and_auth(gateway, config)
    try:
        # Send drop_file request for non-existent file
        drop_file_request = RpcRequest(
            jsonrpc="2.0",
            method="drop_file",
            params={"file_path": "nonexistent.py"},
            id=3,
        )
        await ws.send(drop_file_request.model_dump_json())

        # Receive error response
        response_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        response = json.loads(response_raw)

        assert response["id"] == 3
        assert response.get("error") is not None
        assert response.get("error", {}).get("code") == -32001
        assert "file not found" in response.get("error", {}).get("message", "")
        assert response.get("result") is None
    finally:
        await ws.close()


@pytest.mark.asyncio
async def test_drop_file_missing_param_over_ws(gateway: GatewayService, config: Any) -> None:
    """Test drop_file request with missing file_path parameter."""
    ws = await _connect_and_auth(gateway, config)
    try:
        # Send drop_file request without file_path
        drop_file_request = RpcRequest(
            jsonrpc="2.0",
            method="drop_file",
            params={},
            id=4,
        )
        await ws.send(drop_file_request.model_dump_json())

        # Receive error response
        response_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        response = json.loads(response_raw)

        assert response["id"] == 4
        assert response.get("error") is not None
        assert response.get("error", {}).get("code") == -32601
    finally:
        await ws.close()


@pytest.mark.asyncio
async def test_drop_file_wildcard_pattern_over_ws(gateway: GatewayService, config: Any) -> None:
    """Test drop_file request with wildcard pattern."""
    ws = await _connect_and_auth(gateway, config)
    try:
        # Send add_file request
        add_file_request = RpcRequest(
            jsonrpc="2.0",
            method="add_file",
            params={"file_path": "README.md"},
            id=2,
        )
        await ws.send(add_file_request.model_dump_json())

        # Receive response
        response_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)

        # Send drop_file request with wildcard pattern
        drop_file_request = RpcRequest(
            jsonrpc="2.0",
            method="drop_file",
            params={"file_path": "*.md"},
            id=5,
        )
        await ws.send(drop_file_request.model_dump_json())

        # Receive response
        response_raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        response = json.loads(response_raw)

        assert response["id"] == 5
        assert response.get("result", {}).get("ok") is True
        assert response.get("result", {}).get("file_path") == "*.md"
    finally:
        await ws.close()
