from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestSessionContextService(BaseTest):
    """Test suite for SessionContextService."""

    @pytest.fixture
    def providers(self):
        """Provide KnowledgeServiceProvider for session context tests."""
        from byte.knowledge import KnowledgeServiceProvider

        return [KnowledgeServiceProvider]

    @pytest.mark.asyncio
    async def test_add_context_adds_model_to_store(self, application: Application):
        """Test adding a context model to the session store."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)
        model = application.make(SessionContextModel, type="file", key="test_key", content="test content")

        # Add context
        result = service.add_context(model)

        # Should return self for chaining
        assert result is service

        # Should be in store
        assert service.get_context("test_key") is not None

    @pytest.mark.asyncio
    async def test_remove_context_removes_model_from_store(self, application: Application):
        """Test removing a context model from the session store."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)
        model = application.make(SessionContextModel, type="file", key="to_remove", content="content")

        # Add then remove
        service.add_context(model)
        result = service.remove_context("to_remove")

        # Should return self for chaining
        assert result is service

        # Should be removed
        assert service.get_context("to_remove") is None

    @pytest.mark.asyncio
    async def test_remove_context_deletes_file(self, application: Application):
        """Test that removing context deletes the underlying file."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)
        model = application.make(SessionContextModel, type="file", key="delete_test", content="content")

        # Add context
        service.add_context(model)

        # Verify file exists
        assert model.file_path.exists()

        # Remove context
        service.remove_context("delete_test")

        # File should be deleted
        assert not model.file_path.exists()

    @pytest.mark.asyncio
    async def test_get_context_returns_model(self, application: Application):
        """Test retrieving a specific context model from the store."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)
        model = application.make(SessionContextModel, type="web", key="get_test", content="test content")

        # Add context
        service.add_context(model)

        # Get context
        retrieved = service.get_context("get_test")

        # Should return the model
        assert retrieved is not None
        assert retrieved.key == "get_test"
        assert retrieved.type == "web"

    @pytest.mark.asyncio
    async def test_get_context_returns_none_for_missing_key(self, application: Application):
        """Test that getting nonexistent context returns None."""
        from byte.knowledge import SessionContextService

        service = application.make(SessionContextService)

        # Get nonexistent context
        result = service.get_context("nonexistent")

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_clear_context_removes_all_models(self, application: Application):
        """Test clearing all context models from the session store."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)

        # Add multiple contexts
        model1 = application.make(SessionContextModel, type="file", key="clear1", content="content1")
        model2 = application.make(SessionContextModel, type="web", key="clear2", content="content2")

        service.add_context(model1)
        service.add_context(model2)

        # Verify they exist
        assert len(service.get_all_context()) == 2

        # Clear all
        result = service.clear_context()

        # Should return self for chaining
        assert result is service

        # Should be empty
        assert len(service.get_all_context()) == 0

    @pytest.mark.asyncio
    async def test_clear_context_deletes_all_files(self, application: Application):
        """Test that clearing context deletes all underlying files."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)

        # Add multiple contexts
        model1 = application.make(SessionContextModel, type="file", key="delete1", content="content1")
        model2 = application.make(SessionContextModel, type="file", key="delete2", content="content2")

        service.add_context(model1)
        service.add_context(model2)

        # Verify files exist
        assert model1.file_path.exists()
        assert model2.file_path.exists()

        # Clear all
        service.clear_context()

        # Files should be deleted
        assert not model1.file_path.exists()
        assert not model2.file_path.exists()

    @pytest.mark.asyncio
    async def test_get_all_context_returns_all_models(self, application: Application):
        """Test retrieving all context models from the session store."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)

        # Add multiple contexts
        model1 = application.make(SessionContextModel, type="file", key="all1", content="content1")
        model2 = application.make(SessionContextModel, type="web", key="all2", content="content2")

        service.add_context(model1)
        service.add_context(model2)

        # Get all contexts
        all_contexts = service.get_all_context()

        # Should return dict with all models
        assert isinstance(all_contexts, dict)
        assert len(all_contexts) == 2
        assert "all1" in all_contexts
        assert "all2" in all_contexts

    @pytest.mark.asyncio
    async def test_add_session_context_hook_adds_contexts_to_payload(self, application: Application):
        """Test that hook adds session contexts to payload."""
        from byte import Payload
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)

        # Add context
        model = application.make(SessionContextModel, type="file", key="hook_test", content="hook content")
        service.add_context(model)

        # Create payload
        payload = Payload(event_type="test")

        # Call hook
        result = await service.add_session_context_hook(payload)

        # Should have session_docs in payload
        session_docs = result.get("session_docs", [])
        assert len(session_docs) > 0
        assert any("hook_test" in str(doc) for doc in session_docs)

    @pytest.mark.asyncio
    async def test_add_session_context_hook_handles_empty_context(self, application: Application):
        """Test that hook handles empty context gracefully."""
        from byte import Payload
        from byte.knowledge import SessionContextService

        service = application.make(SessionContextService)
        service.clear_context()

        # Create payload
        payload = Payload(event_type="test")

        # Call hook
        result = await service.add_session_context_hook(payload)

        # Should not add session_docs key if empty
        session_docs = result.get("session_docs", [])
        assert len(session_docs) == 0

    @pytest.mark.asyncio
    async def test_session_context_includes_boundary_tags(self, application: Application):
        """Test that session context includes proper boundary tags."""
        from byte import Payload
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)

        # Add context
        model = application.make(SessionContextModel, type="web", key="tagged", content="tagged content")
        service.add_context(model)

        # Create payload and call hook
        payload = Payload(event_type="test")
        result = await service.add_session_context_hook(payload)

        # Get session docs
        session_docs = result.get("session_docs", [])
        assert len(session_docs) > 0

        # Should include boundary tags
        content = session_docs[0]
        assert "<session_context" in content
        assert "</session_context>" in content

    @pytest.mark.asyncio
    async def test_session_context_includes_metadata(self, application: Application):
        """Test that session context includes type and key metadata."""
        from byte import Payload
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)

        # Add context
        model = application.make(SessionContextModel, type="agent", key="metadata_test", content="content")
        service.add_context(model)

        # Create payload and call hook
        payload = Payload(event_type="test")
        result = await service.add_session_context_hook(payload)

        # Get session docs
        session_docs = result.get("session_docs", [])
        content = session_docs[0]

        # Should include metadata
        assert "type=" in content
        assert "agent" in content
        assert "key=" in content
        assert "metadata_test" in content

    @pytest.mark.asyncio
    async def test_add_context_with_file_type(self, application: Application):
        """Test adding context with file type."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)
        model = application.make(SessionContextModel, type="file", key="file_test", content="file content")

        service.add_context(model)

        # Should be added with correct type
        retrieved = service.get_context("file_test")
        assert retrieved.type == "file"

    @pytest.mark.asyncio
    async def test_add_context_with_web_type(self, application: Application):
        """Test adding context with web type."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)
        model = application.make(SessionContextModel, type="web", key="web_test", content="web content")

        service.add_context(model)

        # Should be added with correct type
        retrieved = service.get_context("web_test")
        assert retrieved.type == "web"

    @pytest.mark.asyncio
    async def test_add_context_with_agent_type(self, application: Application):
        """Test adding context with agent type."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)
        model = application.make(SessionContextModel, type="agent", key="agent_test", content="agent content")

        service.add_context(model)

        # Should be added with correct type
        retrieved = service.get_context("agent_test")
        assert retrieved.type == "agent"

    @pytest.mark.asyncio
    async def test_multiple_contexts_in_hook_payload(self, application: Application):
        """Test that hook includes all contexts in payload."""
        from byte import Payload
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)

        # Add multiple contexts
        model1 = application.make(SessionContextModel, type="file", key="multi1", content="content1")
        model2 = application.make(SessionContextModel, type="web", key="multi2", content="content2")
        model3 = application.make(SessionContextModel, type="agent", key="multi3", content="content3")

        service.add_context(model1)
        service.add_context(model2)
        service.add_context(model3)

        # Create payload and call hook
        payload = Payload(event_type="test")
        result = await service.add_session_context_hook(payload)

        # Should have all contexts
        session_docs = result.get("session_docs", [])
        assert len(session_docs) == 3

    @pytest.mark.asyncio
    async def test_add_context_returns_self_for_chaining(self, application: Application):
        """Test that add_context returns self for method chaining."""
        from byte.knowledge import SessionContextModel, SessionContextService

        service = application.make(SessionContextService)
        model = application.make(SessionContextModel, type="file", key="chain_test", content="content")

        # Should return self
        result = service.add_context(model)
        assert result is service

    @pytest.mark.asyncio
    async def test_remove_context_returns_self_for_chaining(self, application: Application):
        """Test that remove_context returns self for method chaining."""
        from byte.knowledge import SessionContextService

        service = application.make(SessionContextService)

        # Should return self
        result = service.remove_context("any_key")
        assert result is service

    @pytest.mark.asyncio
    async def test_clear_context_returns_self_for_chaining(self, application: Application):
        """Test that clear_context returns self for method chaining."""
        from byte.knowledge import SessionContextService

        service = application.make(SessionContextService)

        # Should return self
        result = service.clear_context()
        assert result is service
