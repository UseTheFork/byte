"""Test suite for LSPService."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide LSPServiceProvider for LSP service tests."""
    from byte.lsp import LSPServiceProvider

    return [LSPServiceProvider]


@pytest.mark.asyncio
async def test_service_boots_without_errors(application: Application):
    """Test that LSP service can be instantiated and booted."""
    from byte.lsp import LSPService

    lsp_service = application.make(LSPService)

    # Service should be instantiated
    assert lsp_service is not None
    assert isinstance(lsp_service.clients, dict)
    assert isinstance(lsp_service.language_map, dict)


@pytest.mark.asyncio
async def test_language_map_empty_when_no_servers_configured(application: Application):
    """Test that language_map is empty when no LSP servers are configured."""
    from byte.lsp import LSPService

    lsp_service = application.make(LSPService)

    # With no servers configured, language_map should be empty
    assert len(lsp_service.language_map) == 0
    assert len(lsp_service.clients) == 0


@pytest.mark.asyncio
async def test_get_client_for_file_returns_none_when_lsp_disabled(application: Application):
    """Test that _get_client_for_file returns None when LSP is disabled."""
    from pathlib import Path

    from byte.lsp import LSPService

    lsp_service = application.make(LSPService)

    # Create a test Python file
    test_file = application.base_path("test.py")
    test_file.write_text("print('hello')")

    # Should return None when LSP is disabled
    client = await lsp_service._get_client_for_file(Path(test_file))
    assert client is None
