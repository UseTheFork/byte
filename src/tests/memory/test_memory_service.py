from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestMemoryService(BaseTest):
    """Test suite for MemoryService."""

    @pytest.fixture
    def providers(self):
        """Provide MemoryServiceProvider for memory service tests."""
        from byte.memory import MemoryServiceProvider

        return [MemoryServiceProvider]

    @pytest.mark.asyncio
    async def test_get_checkpointer_returns_in_memory_saver(self, application: Application):
        """Test that get_checkpointer returns an InMemorySaver instance."""
        from langgraph.checkpoint.memory import InMemorySaver

        from byte.memory import MemoryService

        service = application.make(MemoryService)
        checkpointer = await service.get_checkpointer()

        assert checkpointer is not None
        assert isinstance(checkpointer, InMemorySaver)

    @pytest.mark.asyncio
    async def test_get_checkpointer_returns_same_instance(self, application: Application):
        """Test that get_checkpointer returns the same instance on multiple calls."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        checkpointer1 = await service.get_checkpointer()
        checkpointer2 = await service.get_checkpointer()

        assert checkpointer1 is checkpointer2

    @pytest.mark.asyncio
    async def test_get_saver_returns_checkpointer(self, application: Application):
        """Test that get_saver returns the same instance as get_checkpointer."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        saver = await service.get_saver()
        checkpointer = await service.get_checkpointer()

        assert saver is checkpointer

    @pytest.mark.asyncio
    async def test_create_thread_returns_unique_id(self, application: Application):
        """Test that create_thread returns a unique thread identifier."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        thread_id = service.create_thread()

        assert thread_id is not None
        assert isinstance(thread_id, str)
        assert len(thread_id) > 0

    @pytest.mark.asyncio
    async def test_create_thread_returns_different_ids(self, application: Application):
        """Test that create_thread returns different IDs on multiple calls."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        thread_id1 = service.create_thread()
        thread_id2 = service.create_thread()

        assert thread_id1 != thread_id2

    @pytest.mark.asyncio
    async def test_set_current_thread_stores_thread_id(self, application: Application):
        """Test that set_current_thread stores the provided thread ID."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        thread_id = "test-thread-123"
        await service.set_current_thread(thread_id)

        assert service.get_current_thread() == thread_id

    @pytest.mark.asyncio
    async def test_get_current_thread_returns_none_initially(self, application: Application):
        """Test that get_current_thread returns None when no thread is set."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        current_thread = service.get_current_thread()

        assert current_thread is None

    @pytest.mark.asyncio
    async def test_get_current_thread_returns_set_thread(self, application: Application):
        """Test that get_current_thread returns the thread ID that was set."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        thread_id = "test-thread-456"
        await service.set_current_thread(thread_id)

        assert service.get_current_thread() == thread_id

    @pytest.mark.asyncio
    async def test_get_or_create_thread_creates_thread_when_none_exists(self, application: Application):
        """Test that get_or_create_thread creates a new thread when none exists."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        thread_id = await service.get_or_create_thread()

        assert thread_id is not None
        assert isinstance(thread_id, str)
        assert len(thread_id) > 0

    @pytest.mark.asyncio
    async def test_get_or_create_thread_returns_existing_thread(self, application: Application):
        """Test that get_or_create_thread returns existing thread when one is set."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        original_thread_id = "existing-thread-789"
        await service.set_current_thread(original_thread_id)

        thread_id = await service.get_or_create_thread()

        assert thread_id == original_thread_id

    @pytest.mark.asyncio
    async def test_get_or_create_thread_sets_current_thread(self, application: Application):
        """Test that get_or_create_thread sets the current thread when creating new one."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        thread_id = await service.get_or_create_thread()

        assert service.get_current_thread() == thread_id

    @pytest.mark.asyncio
    async def test_new_thread_creates_and_sets_thread(self, application: Application):
        """Test that new_thread creates a new thread and sets it as current."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        thread_id = await service.new_thread()

        assert thread_id is not None
        assert service.get_current_thread() == thread_id

    @pytest.mark.asyncio
    async def test_new_thread_replaces_existing_thread(self, application: Application):
        """Test that new_thread replaces the existing current thread."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        old_thread_id = await service.new_thread()
        new_thread_id = await service.new_thread()

        assert new_thread_id != old_thread_id
        assert service.get_current_thread() == new_thread_id

    @pytest.mark.asyncio
    async def test_new_thread_returns_unique_ids(self, application: Application):
        """Test that new_thread returns different IDs on multiple calls."""
        from byte.memory import MemoryService

        service = application.make(MemoryService)
        thread_id1 = await service.new_thread()
        thread_id2 = await service.new_thread()

        assert thread_id1 != thread_id2
