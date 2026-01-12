from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestConventionContextService(BaseTest):
    """Test suite for ConventionContextService."""

    @pytest.fixture
    def providers(self):
        """Provide KnowledgeServiceProvider for convention context tests."""
        from byte.knowledge import KnowledgeServiceProvider

        return [KnowledgeServiceProvider]

    @pytest.mark.asyncio
    async def test_loads_conventions_from_directory_on_boot(self, application: Application):
        """Test that conventions are loaded from conventions directory during boot."""
        from byte.knowledge import ConventionContextService

        # Create convention files
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention1 = application.conventions_path("style_guide.md")
        convention1.write_text("# Style Guide\n\nFollow PEP 8")

        convention2 = application.conventions_path("architecture.md")
        convention2.write_text("# Architecture\n\nUse clean architecture")

        await asyncio.sleep(0.2)

        # Create service and refresh to load new files
        service = application.make(ConventionContextService)
        service.refresh()

        # Should have loaded both conventions
        conventions = service.get_conventions()
        assert len(conventions) == 2
        assert "style_guide.md" in conventions
        assert "architecture.md" in conventions

    @pytest.mark.asyncio
    async def test_handles_missing_conventions_directory(self, application: Application):
        """Test that service handles missing conventions directory gracefully."""
        from byte.knowledge import ConventionContextService

        # Remove conventions directory if it exists
        conventions_dir = application.conventions_path()
        if conventions_dir.exists():
            import shutil

            shutil.rmtree(conventions_dir)

        # Create service - should not raise exception
        service = application.make(ConventionContextService)

        # Should have no conventions
        conventions = service.get_conventions()
        assert len(conventions) == 0

    @pytest.mark.asyncio
    async def test_add_convention_loads_file(self, application: Application):
        """Test adding a convention file to the store."""
        from byte.knowledge import ConventionContextService

        # Create convention file
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention_file = conventions_dir / "new_convention.md"
        convention_file.write_text("# New Convention\n\nContent here")
        await asyncio.sleep(0.2)

        service = application.make(ConventionContextService)
        initial_count = len(service.get_conventions())

        # Add convention
        service.add_convention("new_convention.md")

        # Should be added
        conventions = service.get_conventions()
        assert len(conventions) == initial_count + 1
        assert "new_convention.md" in conventions

    @pytest.mark.asyncio
    async def test_add_convention_handles_nonexistent_file(self, application: Application):
        """Test that adding nonexistent convention file is handled gracefully."""
        from byte.knowledge import ConventionContextService

        service = application.make(ConventionContextService)
        initial_count = len(service.get_conventions())

        # Try to add nonexistent file
        service.add_convention("nonexistent.md")

        # Should not add anything
        conventions = service.get_conventions()
        assert len(conventions) == initial_count

    @pytest.mark.asyncio
    async def test_drop_convention_removes_from_store(self, application: Application):
        """Test removing a convention from the store."""
        from byte.knowledge import ConventionContextService

        # Create convention file
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention_file = conventions_dir / "to_remove.md"
        convention_file.write_text("# To Remove\n\nContent")

        service = application.make(ConventionContextService)
        service.refresh()

        # Verify it's loaded
        assert "to_remove.md" in service.get_conventions()

        # Remove it
        service.drop_convention("to_remove.md")

        # Should be removed
        conventions = service.get_conventions()
        assert "to_remove.md" not in conventions

    @pytest.mark.asyncio
    async def test_clear_conventions_removes_all(self, application: Application):
        """Test clearing all conventions from the store."""
        from byte.knowledge import ConventionContextService

        # Create convention files
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention1 = conventions_dir / "conv1.md"
        convention1.write_text("# Convention 1")

        convention2 = conventions_dir / "conv2.md"
        convention2.write_text("# Convention 2")

        await asyncio.sleep(0.2)

        service = application.make(ConventionContextService)
        service.refresh()

        # Verify conventions are loaded
        assert len(service.get_conventions()) >= 2

        # Clear all
        service.clear_conventions()

        # Should be empty
        conventions = service.get_conventions()
        assert len(conventions) == 0

    @pytest.mark.asyncio
    async def test_get_conventions_returns_all_conventions(self, application: Application):
        """Test getting all conventions from the store."""
        from byte.knowledge import ConventionContextService

        # Create convention files
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention1 = conventions_dir / "test1.md"
        convention1.write_text("# Test 1")

        convention2 = conventions_dir / "test2.md"
        convention2.write_text("# Test 2")

        service = application.make(ConventionContextService)
        service.refresh()

        # Get all conventions
        conventions = service.get_conventions()

        # Should return dict with all conventions
        assert isinstance(conventions, dict)
        assert len(conventions) >= 2
        assert "test1.md" in conventions
        assert "test2.md" in conventions

    @pytest.mark.asyncio
    async def test_convention_content_includes_boundary_tags(self, application: Application):
        """Test that convention content includes proper boundary tags."""
        from byte.knowledge import ConventionContextService

        # Create convention file
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention_file = conventions_dir / "tagged.md"
        convention_file.write_text("# Tagged Convention")

        service = application.make(ConventionContextService)
        service.refresh()

        # Get conventions
        conventions = service.get_conventions()
        content = conventions.get("tagged.md", "")

        # Should include boundary tags
        assert "<convention" in content
        assert "</convention>" in content
        assert "```markdown" in content

    @pytest.mark.asyncio
    async def test_convention_content_includes_metadata(self, application: Application):
        """Test that convention content includes title and source metadata."""
        from byte.knowledge import ConventionContextService

        # Create convention file
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention_file = conventions_dir / "metadata_test.md"
        convention_file.write_text("# Metadata Test")

        service = application.make(ConventionContextService)
        service.refresh()

        # Get conventions
        conventions = service.get_conventions()
        content = conventions.get("metadata_test.md", "")

        # Should include metadata
        assert "title=" in content
        assert "Metadata_Test.Md" in content
        assert "source=" in content

    @pytest.mark.asyncio
    async def test_add_project_context_hook_adds_conventions_to_payload(self, application: Application):
        """Test that hook adds conventions to payload."""
        from byte import Payload
        from byte.knowledge import ConventionContextService

        # Create convention file
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention_file = conventions_dir / "hook_test.md"
        convention_file.write_text("# Hook Test")

        service = application.make(ConventionContextService)
        service.refresh()

        # Create payload
        payload = Payload(event_type="test")

        # Call hook
        result = await service.add_project_context_hook(payload)

        # Should have conventions in payload
        conventions_list = result.get("conventions", [])
        assert len(conventions_list) > 0
        assert any("hook_test.md" in str(conv) for conv in conventions_list)

    @pytest.mark.asyncio
    async def test_add_project_context_hook_handles_empty_conventions(self, application: Application):
        """Test that hook handles empty conventions gracefully."""
        from byte import Payload
        from byte.knowledge import ConventionContextService

        service = application.make(ConventionContextService)
        service.clear_conventions()

        # Create payload
        payload = Payload(event_type="test")

        # Call hook
        result = await service.add_project_context_hook(payload)

        # Should not add conventions key if empty
        conventions_list = result.get("conventions", [])
        assert len(conventions_list) == 0

    @pytest.mark.asyncio
    async def test_conventions_sorted_alphabetically(self, application: Application):
        """Test that conventions are loaded in sorted order."""
        from byte.knowledge import ConventionContextService

        # Create convention files with names that would sort differently
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention_c = conventions_dir / "c_convention.md"
        convention_c.write_text("# C")

        convention_a = conventions_dir / "a_convention.md"
        convention_a.write_text("# A")

        convention_b = conventions_dir / "b_convention.md"
        convention_b.write_text("# B")

        service = application.make(ConventionContextService)
        service.refresh()

        # Get conventions
        conventions = service.get_conventions()
        keys = list(conventions.keys())

        # Should be sorted
        assert keys.index("a_convention.md") < keys.index("b_convention.md")
        assert keys.index("b_convention.md") < keys.index("c_convention.md")

    @pytest.mark.asyncio
    async def test_handles_convention_files_with_read_errors(self, application: Application):
        """Test that service handles files that can't be read."""
        import os

        from byte.knowledge import ConventionContextService

        # Create convention file and remove read permissions
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        unreadable_file = conventions_dir / "unreadable.md"
        unreadable_file.write_text("# Unreadable")
        os.chmod(unreadable_file, 0o000)

        try:
            # Create service - should not raise exception
            service = application.make(ConventionContextService)
            service.refresh()

            # Should not include unreadable file
            conventions = service.get_conventions()
            assert "unreadable.md" not in conventions
        finally:
            # Restore permissions for cleanup
            os.chmod(unreadable_file, 0o644)

    @pytest.mark.asyncio
    async def test_only_loads_markdown_files(self, application: Application):
        """Test that only .md files are loaded as conventions."""
        from byte.knowledge import ConventionContextService

        # Create files with different extensions
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        md_file = conventions_dir / "convention.md"
        md_file.write_text("# Markdown Convention")

        txt_file = conventions_dir / "not_convention.txt"
        txt_file.write_text("# Text File")

        py_file = conventions_dir / "script.py"
        py_file.write_text("# Python File")

        service = application.make(ConventionContextService)
        service.refresh()

        # Should only load .md file
        conventions = service.get_conventions()
        assert "convention.md" in conventions
        assert "not_convention.txt" not in conventions
        assert "script.py" not in conventions

    @pytest.mark.asyncio
    async def test_add_convention_returns_self_for_chaining(self, application: Application):
        """Test that add_convention returns self for method chaining."""
        from byte.knowledge import ConventionContextService

        # Create convention file
        conventions_dir = application.conventions_path()
        conventions_dir.mkdir(parents=True, exist_ok=True)

        convention_file = conventions_dir / "chain_test.md"
        convention_file.write_text("# Chain Test")

        service = application.make(ConventionContextService)

        # Should return self
        result = service.add_convention("chain_test.md")
        assert result is service

    @pytest.mark.asyncio
    async def test_drop_convention_returns_self_for_chaining(self, application: Application):
        """Test that drop_convention returns self for method chaining."""
        from byte.knowledge import ConventionContextService

        service = application.make(ConventionContextService)

        # Should return self
        result = service.drop_convention("any_key")
        assert result is service

    @pytest.mark.asyncio
    async def test_clear_conventions_returns_self_for_chaining(self, application: Application):
        """Test that clear_conventions returns self for method chaining."""
        from byte.knowledge import ConventionContextService

        service = application.make(ConventionContextService)

        # Should return self
        result = service.clear_conventions()
        assert result is service
