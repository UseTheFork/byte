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
        pyc_file = application.base_path("test.pyc")
        pyc_file.write_text("compiled python")

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
        test_file1 = application.base_path("test_module.py")
        test_file1.write_text("# test module")

        test_file2 = application.base_path("another_test.py")
        test_file2.write_text("# another test")

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
        new_file = application.base_path("dynamic_file.txt")
        new_file.write_text("dynamic content")

        discovery_service = application.make(FileDiscoveryService)

        # Add file to cache
        result = await discovery_service.add_file(Path(new_file))
        assert result is True

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
        custom_dir = application.base_path("custom_ignored_dir")
        custom_dir.mkdir()
        ignored_file = custom_dir / "should_be_ignored.txt"
        ignored_file.write_text("ignored content")

        # Refresh discovery to pick up new patterns and files
        discovery_service = application.make(FileDiscoveryService)
        await discovery_service.refresh()

        files = await discovery_service.get_files()
        file_names = [f.name for f in files]

        # File in custom ignored directory should not be discovered
        assert "should_be_ignored.txt" not in file_names
