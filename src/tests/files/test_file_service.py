from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestFileService(BaseTest):
    """Test suite for FileService."""

    @pytest.fixture
    def providers(self):
        """Provide FileServiceProvider for file service tests."""
        from byte.files import FileServiceProvider

        return [FileServiceProvider]

    @pytest.mark.asyncio
    async def test_add_file_with_editable_mode(self, application: Application):
        """Test adding a file to context with editable mode."""
        from byte.files import FileMode, FileService

        # Create a test file
        test_file = application.base_path("test_editable.py")
        test_file.write_text("# test file")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        result = await file_service.add_file(test_file, FileMode.EDITABLE)

        assert result is True
        assert await file_service.is_file_in_context(test_file) is True

        # Verify mode is correct
        context = file_service.get_file_context(test_file)
        assert context is not None
        assert context.mode == FileMode.EDITABLE

    @pytest.mark.asyncio
    async def test_add_file_with_read_only_mode(self, application: Application):
        """Test adding a file to context with read-only mode."""
        from byte.files import FileMode, FileService

        # Create a test file
        test_file = application.base_path("test_readonly.py")
        test_file.write_text("# test file")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        result = await file_service.add_file(test_file, FileMode.READ_ONLY)

        assert result is True
        assert await file_service.is_file_in_context(test_file) is True

        # Verify mode is correct
        context = file_service.get_file_context(test_file)
        assert context is not None
        assert context.mode == FileMode.READ_ONLY

    @pytest.mark.asyncio
    async def test_add_file_returns_false_for_nonexistent_file(self, application: Application):
        """Test that adding a nonexistent file returns False."""
        from byte.files import FileMode, FileService

        file_service = application.make(FileService)
        nonexistent = application.base_path("nonexistent.py")

        result = await file_service.add_file(nonexistent, FileMode.EDITABLE)

        assert result is False
        assert await file_service.is_file_in_context(nonexistent) is False

    @pytest.mark.asyncio
    async def test_add_file_returns_false_for_already_added_file(self, application: Application):
        """Test that adding a file twice returns False on second attempt."""
        from byte.files import FileMode, FileService

        # Create a test file
        test_file = application.base_path("duplicate.py")
        test_file.write_text("# test file")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)

        # First add should succeed
        result1 = await file_service.add_file(test_file, FileMode.EDITABLE)
        assert result1 is True

        # Second add should fail
        result2 = await file_service.add_file(test_file, FileMode.EDITABLE)
        assert result2 is False

    @pytest.mark.asyncio
    async def test_add_file_with_wildcard_pattern(self, application: Application):
        """Test adding multiple files using wildcard pattern."""
        from byte.files import FileMode, FileService

        # Create multiple test files
        test_files = ["test1.py", "test2.py", "test3.py"]
        for filename in test_files:
            file_path = application.base_path(filename)
            file_path.write_text(f"# {filename}")
            await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        result = await file_service.add_file("test*.py", FileMode.EDITABLE)

        assert result is True

        # All matching files should be in context
        for filename in test_files:
            file_path = application.base_path(filename)
            assert await file_service.is_file_in_context(file_path) is True

    @pytest.mark.asyncio
    async def test_add_file_wildcard_returns_false_for_no_matches(self, application: Application):
        """Test that wildcard pattern with no matches returns False."""
        from byte.files import FileMode, FileService

        file_service = application.make(FileService)
        result = await file_service.add_file("nonexistent*.py", FileMode.EDITABLE)

        assert result is False

    @pytest.mark.asyncio
    async def test_remove_file_from_context(self, application: Application):
        """Test removing a file from context."""
        from byte.files import FileMode, FileService

        # Create and add a test file
        test_file = application.base_path("to_remove.py")
        test_file.write_text("# test file")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Verify file is in context
        assert await file_service.is_file_in_context(test_file) is True

        # Remove file
        result = await file_service.remove_file(test_file)

        assert result is True
        assert await file_service.is_file_in_context(test_file) is False

    @pytest.mark.asyncio
    async def test_remove_file_returns_false_for_file_not_in_context(self, application: Application):
        """Test that removing a file not in context returns False."""
        from byte.files import FileService

        file_service = application.make(FileService)
        test_file = application.base_path("not_in_context.py")

        result = await file_service.remove_file(test_file)

        assert result is False

    @pytest.mark.asyncio
    async def test_remove_file_with_wildcard_pattern(self, application: Application):
        """Test removing multiple files using wildcard pattern."""
        from byte.files import FileMode, FileService

        # Create and add multiple test files
        test_files = ["remove1.py", "remove2.py", "remove3.py"]
        for filename in test_files:
            file_path = application.base_path(filename)
            file_path.write_text(f"# {filename}")
            await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file("remove*.py", FileMode.EDITABLE)

        # Verify all files are in context
        for filename in test_files:
            file_path = application.base_path(filename)
            assert await file_service.is_file_in_context(file_path) is True

        # Remove all matching files
        result = await file_service.remove_file("remove*.py")

        assert result is True

        # All files should be removed from context
        for filename in test_files:
            file_path = application.base_path(filename)
            assert await file_service.is_file_in_context(file_path) is False

    @pytest.mark.asyncio
    async def test_list_files_returns_all_files(self, application: Application):
        """Test listing all files in context."""
        from byte.files import FileMode, FileService

        # Create and add test files with different modes
        editable_file = application.base_path("editable.py")
        editable_file.write_text("# editable")
        await asyncio.sleep(0.2)

        readonly_file = application.base_path("readonly.py")
        readonly_file.write_text("# readonly")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(editable_file, FileMode.EDITABLE)
        await file_service.add_file(readonly_file, FileMode.READ_ONLY)

        # List all files
        all_files = file_service.list_files()

        assert len(all_files) == 2
        file_names = [f.path.name for f in all_files]
        assert "editable.py" in file_names
        assert "readonly.py" in file_names

    @pytest.mark.asyncio
    async def test_list_files_filtered_by_mode(self, application: Application):
        """Test listing files filtered by access mode."""
        from byte.files import FileMode, FileService

        # Create and add test files with different modes
        editable_file = application.base_path("editable.py")
        editable_file.write_text("# editable")
        await asyncio.sleep(0.2)

        readonly_file = application.base_path("readonly.py")
        readonly_file.write_text("# readonly")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(editable_file, FileMode.EDITABLE)
        await file_service.add_file(readonly_file, FileMode.READ_ONLY)

        # List only editable files
        editable_files = file_service.list_files(FileMode.EDITABLE)
        assert len(editable_files) == 1
        assert editable_files[0].path.name == "editable.py"

        # List only read-only files
        readonly_files = file_service.list_files(FileMode.READ_ONLY)
        assert len(readonly_files) == 1
        assert readonly_files[0].path.name == "readonly.py"

    @pytest.mark.asyncio
    async def test_list_files_returns_sorted_by_relative_path(self, application: Application):
        """Test that list_files returns files sorted by relative path."""
        from byte.files import FileMode, FileService

        # Create files in different order
        file_c = application.base_path("c_file.py")
        file_c.write_text("# c")
        await asyncio.sleep(0.2)

        file_a = application.base_path("a_file.py")
        file_a.write_text("# a")
        await asyncio.sleep(0.2)

        file_b = application.base_path("b_file.py")
        file_b.write_text("# b")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(file_c, FileMode.EDITABLE)
        await file_service.add_file(file_a, FileMode.EDITABLE)
        await file_service.add_file(file_b, FileMode.EDITABLE)

        # List should be sorted
        files = file_service.list_files()
        file_names = [f.path.name for f in files]

        assert file_names == ["a_file.py", "b_file.py", "c_file.py"]

    @pytest.mark.asyncio
    async def test_set_file_mode_changes_mode(self, application: Application):
        """Test changing file mode from editable to read-only."""
        from byte.files import FileMode, FileService

        # Create and add file as editable
        test_file = application.base_path("switch_mode.py")
        test_file.write_text("# test file")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Verify initial mode
        context = file_service.get_file_context(test_file)
        assert context.mode == FileMode.EDITABLE

        # Change mode to read-only
        result = await file_service.set_file_mode(test_file, FileMode.READ_ONLY)

        assert result is True

        # Verify mode changed
        context = file_service.get_file_context(test_file)
        assert context.mode == FileMode.READ_ONLY

    @pytest.mark.asyncio
    async def test_set_file_mode_returns_false_for_file_not_in_context(self, application: Application):
        """Test that setting mode for file not in context returns False."""
        from byte.files import FileMode, FileService

        file_service = application.make(FileService)
        test_file = application.base_path("not_in_context.py")

        result = await file_service.set_file_mode(test_file, FileMode.READ_ONLY)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_file_context_returns_context(self, application: Application):
        """Test getting file context metadata."""
        from byte.files import FileMode, FileService

        # Create and add test file
        test_file = application.base_path("context_test.py")
        test_file.write_text("# test file")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Get context
        context = file_service.get_file_context(test_file)

        assert context is not None
        assert context.path == test_file.resolve()
        assert context.mode == FileMode.EDITABLE

    @pytest.mark.asyncio
    async def test_get_file_context_returns_none_for_file_not_in_context(self, application: Application):
        """Test that getting context for file not in context returns None."""
        from byte.files import FileService

        file_service = application.make(FileService)
        test_file = application.base_path("not_in_context.py")

        context = file_service.get_file_context(test_file)

        assert context is None

    @pytest.mark.asyncio
    async def test_generate_context_prompt_with_read_only_files(self, application: Application):
        """Test generating context prompt with read-only files."""
        from byte.files import FileMode, FileService

        # Create and add read-only file
        readonly_file = application.base_path("readonly.py")
        readonly_file.write_text("# readonly content")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(readonly_file, FileMode.READ_ONLY)

        # Generate prompt
        read_only, editable = await file_service.generate_context_prompt()

        assert len(read_only) == 1
        assert len(editable) == 0
        assert "readonly.py" in read_only[0]
        assert "# readonly content" in read_only[0]

    @pytest.mark.asyncio
    async def test_generate_context_prompt_with_editable_files(self, application: Application):
        """Test generating context prompt with editable files."""
        from byte.files import FileMode, FileService

        # Create and add editable file
        editable_file = application.base_path("editable.py")
        editable_file.write_text("# editable content")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(editable_file, FileMode.EDITABLE)

        # Generate prompt
        read_only, editable = await file_service.generate_context_prompt()

        assert len(read_only) == 0
        assert len(editable) == 1
        assert "editable.py" in editable[0]
        assert "# editable content" in editable[0]

    @pytest.mark.asyncio
    async def test_generate_context_prompt_with_mixed_modes(self, application: Application):
        """Test generating context prompt with both read-only and editable files."""
        from byte.files import FileMode, FileService

        # Create and add files with different modes
        readonly_file = application.base_path("readonly.py")
        readonly_file.write_text("# readonly")
        await asyncio.sleep(0.2)

        editable_file = application.base_path("editable.py")
        editable_file.write_text("# editable")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(readonly_file, FileMode.READ_ONLY)
        await file_service.add_file(editable_file, FileMode.EDITABLE)

        # Generate prompt
        read_only, editable = await file_service.generate_context_prompt()

        assert len(read_only) == 1
        assert len(editable) == 1
        assert "readonly.py" in read_only[0]
        assert "editable.py" in editable[0]

    @pytest.mark.asyncio
    async def test_generate_context_prompt_returns_empty_for_no_files(self, application: Application):
        """Test that generating prompt with no files returns empty lists."""
        from byte.files import FileService

        file_service = application.make(FileService)

        # Generate prompt with no files
        read_only, editable = await file_service.generate_context_prompt()

        assert len(read_only) == 0
        assert len(editable) == 0

    @pytest.mark.asyncio
    async def test_clear_context_removes_all_files(self, application: Application):
        """Test clearing all files from context."""
        from byte.files import FileMode, FileService

        # Create and add multiple files
        file1 = application.base_path("file1.py")
        file1.write_text("# file1")
        await asyncio.sleep(0.2)

        file2 = application.base_path("file2.py")
        file2.write_text("# file2")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(file1, FileMode.EDITABLE)
        await file_service.add_file(file2, FileMode.READ_ONLY)

        # Verify files are in context
        assert len(file_service.list_files()) == 2

        # Clear context
        await file_service.clear_context()

        # All files should be removed
        assert len(file_service.list_files()) == 0

    @pytest.mark.asyncio
    async def test_get_project_files_returns_relative_paths(self, application: Application):
        """Test getting all project files as relative paths."""
        from byte.files import FileService

        # Create test files
        test_file = application.base_path("project_file.py")
        test_file.write_text("# project file")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        project_files = await file_service.get_project_files()

        # Should return strings
        assert all(isinstance(path, str) for path in project_files)

        # Should include files from fixture
        assert "README.md" in project_files

    @pytest.mark.asyncio
    async def test_get_project_files_filtered_by_extension(self, application: Application):
        """Test getting project files filtered by extension."""
        from byte.files import FileService

        # Create files with different extensions
        py_file = application.base_path("script.py")
        py_file.write_text("# python")
        await asyncio.sleep(0.2)

        js_file = application.base_path("app.js")
        js_file.write_text("// javascript")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)

        # Get only Python files
        py_files = await file_service.get_project_files(".py")

        # Should only include .py files
        assert any("script.py" in path for path in py_files)
        assert not any("app.js" in path for path in py_files)

    @pytest.mark.asyncio
    async def test_find_project_files_with_pattern(self, application: Application):
        """Test finding project files matching a pattern."""
        from byte.files import FileService

        # Create test files
        test_file = application.base_path("test_module.py")
        test_file.write_text("# test")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        matches = await file_service.find_project_files("test")

        # Should find files with "test" in name
        assert any("test_module.py" in path for path in matches)

    @pytest.mark.asyncio
    async def test_is_file_in_context_returns_true_for_added_file(self, application: Application):
        """Test checking if file is in context."""
        from byte.files import FileMode, FileService

        # Create and add test file
        test_file = application.base_path("in_context.py")
        test_file.write_text("# test")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Should return True
        assert await file_service.is_file_in_context(test_file) is True

    @pytest.mark.asyncio
    async def test_is_file_in_context_returns_false_for_file_not_added(self, application: Application):
        """Test checking if file not in context returns False."""
        from byte.files import FileService

        file_service = application.make(FileService)
        test_file = application.base_path("not_added.py")

        # Should return False
        assert await file_service.is_file_in_context(test_file) is False

    @pytest.mark.asyncio
    async def test_generate_project_hierarchy_returns_tree_structure(self, application: Application):
        """Test generating project hierarchy tree."""
        from byte.files import FileService

        # Create nested directory structure
        src_dir = application.base_path("src")
        src_dir.mkdir()

        utils_dir = src_dir / "utils"
        utils_dir.mkdir()

        main_file = src_dir / "main.py"
        main_file.write_text("# main")
        await asyncio.sleep(0.2)

        helper_file = utils_dir / "helper.py"
        helper_file.write_text("# helper")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        hierarchy = await file_service.generate_project_hierarchy()

        # Should contain directory structure
        assert "Project Structure:" in hierarchy
        assert "src/" in hierarchy
        assert "utils/" in hierarchy

    @pytest.mark.asyncio
    async def test_add_file_only_adds_discovered_files(self, application: Application):
        """Test that add_file only adds files from discovery service."""
        from byte.files import FileMode, FileService

        # Create a file that should be ignored
        ignored_file = application.base_path("ignored.pyc")
        ignored_file.write_text("compiled")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        result = await file_service.add_file(ignored_file, FileMode.EDITABLE)

        # Should return False because file is ignored
        assert result is False
        assert await file_service.is_file_in_context(ignored_file) is False

    @pytest.mark.asyncio
    async def test_remove_file_wildcard_only_removes_discovered_files(self, application: Application):
        """Test that wildcard remove only affects files in discovery service."""
        from byte.files import FileMode, FileService

        # Create and add a valid file
        valid_file = application.base_path("valid.py")
        valid_file.write_text("# valid")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(valid_file, FileMode.EDITABLE)

        # Try to remove with wildcard that would match ignored files too
        result = await file_service.remove_file("*.py")

        # Should succeed and remove valid file
        assert result is True
        assert await file_service.is_file_in_context(valid_file) is False

    @pytest.mark.asyncio
    async def test_generate_context_prompt_includes_language_metadata(self, application: Application):
        """Test that context prompt includes language metadata."""
        from byte.files import FileMode, FileService

        # Create Python file
        py_file = application.base_path("script.py")
        py_file.write_text("# python script")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(py_file, FileMode.EDITABLE)

        # Generate prompt
        _, editable = await file_service.generate_context_prompt()

        # Should include language in metadata
        assert len(editable) == 1
        assert "python" in editable[0].lower()

    @pytest.mark.asyncio
    async def test_generate_context_prompt_handles_unreadable_files(self, application: Application):
        """Test that context prompt handles files that can't be read."""
        import os

        from byte.files import FileMode, FileService

        # Create file and remove read permissions
        unreadable_file = application.base_path("unreadable.py")
        unreadable_file.write_text("secret")
        await asyncio.sleep(0.2)
        os.chmod(unreadable_file, 0o000)

        try:
            file_service = application.make(FileService)
            await file_service.add_file(unreadable_file, FileMode.EDITABLE)

            # Generate prompt should not raise exception
            _, editable = await file_service.generate_context_prompt()

            # Should include error message in content
            assert len(editable) == 1
            assert "ERROR" in editable[0]
        finally:
            # Restore permissions for cleanup
            os.chmod(unreadable_file, 0o644)

    @pytest.mark.asyncio
    async def test_add_file_with_relative_path(self, application: Application):
        """Test adding file using relative path."""
        from byte.files import FileMode, FileService

        # Create test file
        test_file = application.base_path("relative_test.py")
        test_file.write_text("# test")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)

        # Add using relative path
        result = await file_service.add_file("relative_test.py", FileMode.EDITABLE)

        assert result is True
        assert await file_service.is_file_in_context(test_file) is True

    @pytest.mark.asyncio
    async def test_remove_file_with_relative_path(self, application: Application):
        """Test removing file using relative path."""
        from byte.files import FileMode, FileService

        # Create and add test file
        test_file = application.base_path("relative_remove.py")
        test_file.write_text("# test")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Remove using relative path
        result = await file_service.remove_file("relative_remove.py")

        assert result is True
        assert await file_service.is_file_in_context(test_file) is False

    @pytest.mark.asyncio
    async def test_file_context_emits_file_added_event(self, application: Application):
        """Test that adding a file emits FILE_ADDED event."""
        from byte import EventBus, EventType
        from byte.files import FileMode, FileService

        event_bus = application.make(EventBus)
        events_received = []

        async def capture_event(payload):
            events_received.append(payload)
            return payload

        event_bus.on(EventType.FILE_ADDED.value, capture_event)

        # Create and add test file
        test_file = application.base_path("event_test.py")
        test_file.write_text("# test")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Wait for event processing
        await asyncio.sleep(0.1)

        # Should have received FILE_ADDED event
        assert len(events_received) > 0
        event = events_received[0]
        assert event.get("file_path") is not None
        assert event.get("mode") == FileMode.EDITABLE.value

    @pytest.mark.asyncio
    async def test_generate_context_prompt_with_line_numbers(self, application: Application):
        """Test generating context prompt with line numbers."""
        from byte.files import FileMode, FileService

        # Create test file with multiple lines
        test_file = application.base_path("numbered.py")
        test_file.write_text("line 1\nline 2\nline 3")
        await asyncio.sleep(0.2)

        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Generate prompt with line numbers
        _, editable = await file_service.generate_context_prompt_with_line_numbers()

        # Should include line numbers
        assert len(editable) == 1
        assert "1 |" in editable[0] or "   1 |" in editable[0]
        assert "line 1" in editable[0]
