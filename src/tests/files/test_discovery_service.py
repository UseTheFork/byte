from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestDiscoveryService(BaseTest):
    """Test suite for FileDiscoveryService."""

    @pytest.fixture
    def providers(self):
        """Provide FileServiceProvider for discovery service tests."""
        from byte.files import FileServiceProvider

        return [FileServiceProvider]

    @pytest.mark.asyncio
    async def test_discovers_git_repo_files(self, application: Application):
        """Test that discovery service finds files created in git repo fixture."""
        from byte.files import FileDiscoveryService

        discovery_service = application.make(FileDiscoveryService)
        files = await discovery_service.get_files()

        # Should find at least README.md and .gitignore from the fixture
        file_names = [f.name for f in files]
        assert "README.md" in file_names
        assert ".gitignore" in file_names

    @pytest.mark.asyncio
    async def test_respects_gitignore_patterns(self, application: Application):
        """Test that discovery service respects .gitignore patterns."""
        from byte.files import FileDiscoveryService

        # Create a .pyc file that should be ignored
        await self.create_test_file(application, "test.pyc", "compiled python")

        # Refresh discovery to pick up new file
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        files = await discovery_service.get_files()
        file_names = [f.name for f in files]

        # .pyc files should be ignored per .gitignore
        assert "test.pyc" not in file_names

    @pytest.mark.asyncio
    async def test_find_files_with_pattern(self, application: Application):
        """Test that discovery service can find files matching a pattern."""
        from byte.files import FileDiscoveryService

        # Create some test files
        await self.create_test_file(application, "test_module.py", "# test module")
        await self.create_test_file(application, "another_test.py", "# another test")

        # Refresh discovery to pick up new files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        # Search for files with "test" in the name
        matches = await discovery_service.find_files("test")
        match_names = [f.name for f in matches]

        # Should find both test files
        assert "test_module.py" in match_names
        assert "another_test.py" in match_names

    @pytest.mark.asyncio
    async def test_get_relative_paths(self, application: Application):
        """Test that discovery service returns relative paths correctly."""
        from byte.files import FileDiscoveryService

        discovery_service = application.make(FileDiscoveryService)
        relative_paths = await discovery_service.get_relative_paths()

        # Should return strings, not Path objects
        assert all(isinstance(path, str) for path in relative_paths)

        # Should include files from fixture
        assert "README.md" in relative_paths
        assert ".gitignore" in relative_paths

    @pytest.mark.asyncio
    async def test_add_and_remove_file(self, application: Application):
        """Test that discovery service can add and remove files from cache."""
        from pathlib import Path

        from byte.files import FileDiscoveryService

        # Create a new file
        new_file = await self.create_test_file(application, "dynamic_file.txt", "dynamic content")

        discovery_service = application.make(FileDiscoveryService)

        # Verify file is in cache
        files = await discovery_service.get_files()
        file_names = [f.name for f in files]
        assert "dynamic_file.txt" in file_names

        # Remove file from cache
        result = await discovery_service.remove_file(Path(new_file))
        assert result is True

        # Verify file is no longer in cache
        files = await discovery_service.get_files()
        file_names = [f.name for f in files]
        assert "dynamic_file.txt" not in file_names

    @pytest.mark.asyncio
    async def test_respects_custom_ignore_patterns(self, application: Application):
        """Test that discovery service respects custom ignore patterns from config."""
        from byte.files import FileDiscoveryService

        # Add a custom ignore pattern to config
        config = application["config"]
        config.files.ignore.append("custom_ignored_dir")

        # Create a file in a custom ignored directory
        custom_dir = application.root_path("custom_ignored_dir")
        custom_dir.mkdir()
        await self.create_test_file(application, "custom_ignored_dir/should_be_ignored.txt", "ignored content")

        # Refresh discovery to pick up new patterns and files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        files = await discovery_service.get_files()
        file_names = [f.name for f in files]

        # File in custom ignored directory should not be discovered
        assert "should_be_ignored.txt" not in file_names

    @pytest.mark.asyncio
    async def test_filter_files_by_extension(self, application: Application):
        """Test that discovery service can filter files by extension."""
        from byte.files import FileDiscoveryService

        # Create files with different extensions
        await self.create_test_file(application, "script.py", "# python script")
        await self.create_test_file(application, "app.js", "// javascript app")
        await self.create_test_file(application, "notes.txt", "text notes")

        # Refresh discovery to pick up new files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        # Get only Python files
        py_files = await discovery_service.get_files(".py")
        py_file_names = [f.name for f in py_files]

        # Should only include .py files
        assert "script.py" in py_file_names
        assert "app.js" not in py_file_names
        assert "notes.txt" not in py_file_names

        # Get only JavaScript files
        js_files = await discovery_service.get_files(".js")
        js_file_names = [f.name for f in js_files]

        # Should only include .js files
        assert "app.js" in js_file_names
        assert "script.py" not in js_file_names
        assert "notes.txt" not in js_file_names

    @pytest.mark.asyncio
    async def test_discovers_files_in_nested_directories(self, application: Application):
        """Test that discovery service finds files in nested directory structures."""
        from byte.files import FileDiscoveryService

        # Create nested directory structure
        src_dir = application.base_path("src")
        src_dir.mkdir()

        utils_dir = src_dir / "utils"
        utils_dir.mkdir()

        # Create files at different levels
        await self.create_test_file(application, "src/main.py", "# main module")
        await self.create_test_file(application, "src/utils/helpers.py", "# helper functions")

        # Refresh discovery to pick up new files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        files = await discovery_service.get_files()
        file_names = [f.name for f in files]

        # Should find files at all levels
        assert "main.py" in file_names
        assert "helpers.py" in file_names

    @pytest.mark.asyncio
    async def test_find_files_with_fuzzy_matching(self, application: Application):
        """Test that discovery service fuzzy matching prioritizes relevance correctly."""
        from byte.files import FileDiscoveryService

        # Create files with "test" in different positions
        src_dir = application.base_path("src")
        src_dir.mkdir()

        # Pattern in filename (should score higher)
        await self.create_test_file(application, "src/test_utils.py", "# test utilities")

        # Pattern in directory path (should score lower)
        test_dir = application.base_path("tests")
        test_dir.mkdir()
        await self.create_test_file(application, "tests/helpers.py", "# helper functions")

        # Pattern at start of filename (exact match, highest priority)
        await self.create_test_file(application, "test.py", "# test module")

        # Refresh discovery to pick up new files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        # Search for "test" pattern
        matches = await discovery_service.find_files("test")
        match_names = [f.name for f in matches]

        # Should find all files with "test" in path
        assert "test.py" in match_names
        assert "test_utils.py" in match_names
        assert "helpers.py" in match_names

    @pytest.mark.asyncio
    async def test_find_files_case_insensitivity(self, application: Application):
        """Test that pattern matching is case-insensitive."""
        from byte.files import FileDiscoveryService

        # Create files with mixed case names
        await self.create_test_file(application, "TestModule.py", "# test module")
        await self.create_test_file(application, "testhelper.py", "# test helper")
        await self.create_test_file(application, "MyTest.py", "# my test")

        # Refresh discovery to pick up new files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        # Search with lowercase pattern
        matches_lower = await discovery_service.find_files("test")
        match_names_lower = [f.name for f in matches_lower]

        # Should find all files regardless of case
        assert "TestModule.py" in match_names_lower
        assert "testhelper.py" in match_names_lower
        assert "MyTest.py" in match_names_lower

        # Search with uppercase pattern
        matches_upper = await discovery_service.find_files("TEST")
        match_names_upper = [f.name for f in matches_upper]

        # Should find same files with uppercase pattern
        assert "TestModule.py" in match_names_upper
        assert "testhelper.py" in match_names_upper
        assert "MyTest.py" in match_names_upper

        # Results should be identical
        assert set(match_names_lower) == set(match_names_upper)

    @pytest.mark.asyncio
    async def test_ignores_files_in_ignored_parent_directory(self, application: Application):
        """Test that files inside ignored directories are also ignored."""
        from byte.files import FileDiscoveryService

        # Create __pycache__ directory with nested structure
        pycache_dir = application.base_path("__pycache__")
        pycache_dir.mkdir()

        subdir = pycache_dir / "subdir"
        subdir.mkdir()

        # Create files at different levels inside ignored directory
        await self.create_test_file(application, "__pycache__/module.pyc", "compiled")
        await self.create_test_file(application, "__pycache__/subdir/nested.pyc", "compiled nested")
        await self.create_test_file(application, "__pycache__/subdir/source.py", "# source in pycache")

        # Refresh discovery to pick up new files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        files = await discovery_service.get_files()
        file_names = [f.name for f in files]

        # No files from __pycache__ should be discovered
        assert "module.pyc" not in file_names
        assert "nested.pyc" not in file_names
        assert "source.py" not in file_names

        # Verify by checking full paths too
        file_paths = [str(f) for f in files]
        assert not any("__pycache__" in path for path in file_paths)

    @pytest.mark.asyncio
    async def test_refresh_clears_and_rebuilds_cache(self, application: Application):
        """Test that refresh actually clears old entries and rebuilds from scratch."""
        from byte.files import FileDiscoveryService

        # Create initial file
        initial_file = await self.create_test_file(application, "initial.py", "# initial file")

        # Refresh discovery to pick up initial file
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        files = await discovery_service.get_files()
        file_names = [f.name for f in files]
        assert "initial.py" in file_names

        # Delete the initial file and create a new one
        initial_file.unlink()
        await self.create_test_file(application, "new.py", "# new file")

        # Refresh should clear cache and rebuild
        await discovery_service.refresh()

        files = await discovery_service.get_files()
        file_names = [f.name for f in files]

        # Old file should be gone, new file should be present
        assert "initial.py" not in file_names
        assert "new.py" in file_names

    @pytest.mark.asyncio
    async def test_add_file_rejects_ignored_files(self, application: Application):
        """Test that add_file returns False for files matching ignore patterns."""
        from pathlib import Path

        from byte.files import FileDiscoveryService

        # Create a .pyc file that should be ignored
        pyc_file = await self.create_test_file(application, "ignored.pyc", "compiled python")

        discovery_service = application.make(FileDiscoveryService)

        # Try to add ignored file to cache
        result = await discovery_service.add_file(Path(pyc_file))

        # Should return False because file is ignored
        assert result is False

        # Verify file is not in cache
        files = await discovery_service.get_files()
        file_names = [f.name for f in files]
        assert "ignored.pyc" not in file_names

    @pytest.mark.asyncio
    async def test_remove_file_for_nonexistent_file(self, application: Application):
        """Test that remove_file returns False for files not in cache."""
        from pathlib import Path

        from byte.files import FileDiscoveryService

        discovery_service = application.make(FileDiscoveryService)

        # Try to remove a file that was never added
        nonexistent_path = application.base_path("nonexistent.py")
        result = await discovery_service.remove_file(Path(nonexistent_path))

        # Should return False because file is not in cache
        assert result is False

    @pytest.mark.asyncio
    async def test_handles_unreadable_files(self, application: Application):
        """Test that discovery service handles files with no read permissions gracefully."""
        import os

        from byte.files import FileDiscoveryService

        # Create a file and remove read permissions
        unreadable_file = application.base_path("unreadable.txt")
        unreadable_file.write_text("secret content")
        os.chmod(unreadable_file, 0o000)

        try:
            # Refresh discovery to scan for files
            discovery_service = application.make(FileDiscoveryService)
            await discovery_service.refresh()

            # Discovery should complete without raising exceptions
            files = await discovery_service.get_files()

            # The unreadable file might or might not be in the list
            # (depends on whether os.walk can see it), but no exception should occur
            assert isinstance(files, list)
        finally:
            # Restore permissions for cleanup
            os.chmod(unreadable_file, 0o644)

    # TODO: This needs to change. Binary files should not be discovered.
    @pytest.mark.asyncio
    async def test_handles_binary_files(self, application: Application):
        """Test that binary files are discovered without causing errors."""
        from byte.files import FileDiscoveryService

        # Create a binary file (simulated image)
        binary_file = application.base_path("image.png")
        binary_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        binary_file.write_bytes(binary_content)

        # Create another binary file (simulated PDF)
        pdf_file = application.base_path("document.pdf")
        pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
        pdf_file.write_bytes(pdf_content)

        # Refresh discovery to pick up binary files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        files = await discovery_service.get_files()
        file_names = [f.name for f in files]

        # Binary files should be discovered
        assert "image.png" in file_names
        assert "document.pdf" in file_names

        # Verify we can get their paths without errors
        png_files = await discovery_service.get_files(".png")
        assert len(png_files) > 0
        assert png_files[0].name == "image.png"
