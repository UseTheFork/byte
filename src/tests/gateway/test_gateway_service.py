"""Test suite for GatewayService auth handshake."""

import json
from typing import TYPE_CHECKING

import pytest
import websockets

from byte.gateway import GatewayServiceProvider
from byte.gateway.protocol import RpcRequest, RpcResponse

if TYPE_CHECKING:
    from byte import Application
    from byte.gateway import GatewayService


@pytest.fixture
def providers():
    """Provide GatewayServiceProvider for gateway tests."""
    return [GatewayServiceProvider]


@pytest.fixture
async def gateway(application: Application):
    """Start the GatewayService and yield it, then stop on teardown."""
    import asyncio

    from byte.gateway import GatewayService

    service = application.make(GatewayService)

    # Start the server in a background task
    server_task = asyncio.create_task(service.start())

    # Give the server a moment to bind
    await asyncio.sleep(0.1)

    yield service

    await service.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_auth_success(application: Application, gateway: GatewayService):
    """Valid token results in an OK response."""
    config = application["config"].gateway
    url = f"ws://{config.host}:{config.port}"

    async with websockets.connect(url) as ws:
        request = RpcRequest(jsonrpc="2.0", id=1, method="auth", params={"token": gateway._token})
        await ws.send(request.model_dump_json())

        raw = await ws.recv()
        response = RpcResponse.model_validate_json(raw)

        assert response.id == 1
        assert response.result == {"ok": True}


@pytest.mark.asyncio
async def test_auth_invalid_token(application: Application, gateway: GatewayService):
    """Wrong token results in an unauthorized error and closed connection."""
    config = application["config"].gateway
    url = f"ws://{config.host}:{config.port}"

    async with websockets.connect(url) as ws:
        request = RpcRequest(jsonrpc="2.0", id=2, method="auth", params={"token": "wrong-token"})
        await ws.send(request.model_dump_json())

        raw = await ws.recv()
        data = json.loads(raw)

        assert data["error"]["code"] == -32000  # ERR_UNAUTHORIZED


@pytest.mark.asyncio
async def test_auth_wrong_method(application: Application, gateway: GatewayService):
    """Non-auth method on initial connect results in unauthorized error."""
    config = application["config"].gateway
    url = f"ws://{config.host}:{config.port}"

    async with websockets.connect(url) as ws:
        request = RpcRequest(jsonrpc="2.0", id=3, method="execute", params={"input": "hello"})
        await ws.send(request.model_dump_json())

        raw = await ws.recv()
        data = json.loads(raw)

        assert data["error"]["code"] == -32000


@pytest.mark.asyncio
async def test_auth_malformed_request(application: Application, gateway: GatewayService):
    """Malformed JSON results in unauthorized error."""
    config = application["config"].gateway
    url = f"ws://{config.host}:{config.port}"

    async with websockets.connect(url) as ws:
        await ws.send("not valid json at all")

        raw = await ws.recv()
        data = json.loads(raw)

        assert data["error"]["code"] == -32000
