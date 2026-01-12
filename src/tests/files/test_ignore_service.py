from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestIgnoreService(BaseTest):
    """Test suite for FileIgnoreService."""

    @pytest.fixture
    def providers(self):
        """Provide FileServiceProvider for ignore service tests."""
        from byte.files import FileServiceProvider

        return [FileServiceProvider]

    @pytest.mark.asyncio
    async def test_loads_gitignore_patterns(self, application: Application):
        """Test that ignore service loads patterns from .gitignore."""
        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)
        spec = ignore_service.get_pathspec()

        # Should have loaded patterns from .gitignore
        assert spec is not None

    @pytest.mark.asyncio
    async def test_ignores_pyc_files(self, application: Application):
        """Test that .pyc files are ignored per .gitignore."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create a .pyc file path
        pyc_file = application.base_path("test.pyc")

        # Should be ignored
        assert ignore_service.is_ignored(Path(pyc_file)) is True

    @pytest.mark.asyncio
    async def test_ignores_pycache_directory(self, application: Application):
        """Test that __pycache__ directories are ignored."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create __pycache__ directory path
        pycache_dir = application.base_path("__pycache__")

        # Should be ignored
        assert ignore_service.is_ignored(Path(pycache_dir)) is True

    @pytest.mark.asyncio
    async def test_ignores_files_in_pycache_directory(self, application: Application):
        """Test that files inside __pycache__ are ignored."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create file path inside __pycache__
        file_in_pycache = application.base_path("__pycache__/module.pyc")

        # Should be ignored
        assert ignore_service.is_ignored(Path(file_in_pycache)) is True

    @pytest.mark.asyncio
    async def test_does_not_ignore_regular_python_files(self, application: Application):
        """Test that regular .py files are not ignored."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create a regular .py file path
        py_file = application.base_path("script.py")

        # Should not be ignored
        assert ignore_service.is_ignored(Path(py_file)) is False

    @pytest.mark.asyncio
    async def test_respects_custom_ignore_patterns_from_config(self, application: Application):
        """Test that ignore service respects custom patterns from config."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        # Add custom ignore pattern to config
        config = application["config"]
        config.files.ignore.append("custom_ignored_dir")

        # Refresh ignore service to pick up new patterns
        ignore_service = application.make(FileIgnoreService)
        await ignore_service.refresh()

        # Create path in custom ignored directory
        custom_file = application.base_path("custom_ignored_dir/file.txt")

        # Should be ignored
        assert ignore_service.is_ignored(Path(custom_file)) is True

    @pytest.mark.asyncio
    async def test_ignores_pytest_cache(self, application: Application):
        """Test that .pytest_cache directory is ignored."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create .pytest_cache directory path
        pytest_cache = application.base_path(".pytest_cache")

        # Should be ignored
        assert ignore_service.is_ignored(Path(pytest_cache)) is True

    @pytest.mark.asyncio
    async def test_ignores_nested_files_in_ignored_directory(self, application: Application):
        """Test that deeply nested files in ignored directories are ignored."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create deeply nested path in __pycache__
        nested_file = application.base_path("__pycache__/subdir/another/file.pyc")

        # Should be ignored
        assert ignore_service.is_ignored(Path(nested_file)) is True

    @pytest.mark.asyncio
    async def test_refresh_reloads_patterns(self, application: Application):
        """Test that refresh reloads patterns from filesystem and config."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Initially, custom pattern doesn't exist
        custom_file = application.base_path("new_ignored_dir/file.txt")
        assert ignore_service.is_ignored(Path(custom_file)) is False

        # Add new ignore pattern to config
        config = application["config"]
        config.files.ignore.append("new_ignored_dir")

        # Refresh to pick up new pattern
        await ignore_service.refresh()

        # Now should be ignored
        assert ignore_service.is_ignored(Path(custom_file)) is True

    @pytest.mark.asyncio
    async def test_handles_paths_outside_project_root(self, application: Application):
        """Test that paths outside project root are considered ignored."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create path outside project root
        outside_path = Path("/tmp/outside_project/file.py")

        # Should be ignored (outside project root)
        assert ignore_service.is_ignored(outside_path) is True

    @pytest.mark.asyncio
    async def test_get_pathspec_returns_compiled_spec(self, application: Application):
        """Test that get_pathspec returns a valid PathSpec object."""
        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)
        spec = ignore_service.get_pathspec()

        # Should return a PathSpec object
        assert spec is not None
        assert hasattr(spec, "match_file")

    @pytest.mark.asyncio
    async def test_handles_empty_gitignore(self, application: Application, tmp_path):
        """Test that service handles empty .gitignore gracefully."""

        from byte.files import FileIgnoreService

        # Create empty .gitignore
        gitignore = application.base_path(".gitignore")
        gitignore.write_text("")

        # Refresh to reload patterns
        ignore_service = application.make(FileIgnoreService)
        await ignore_service.refresh()

        # Should still work, just with config patterns
        spec = ignore_service.get_pathspec()
        assert spec is not None

    @pytest.mark.asyncio
    async def test_handles_gitignore_with_comments(self, application: Application):
        """Test that service handles .gitignore files with comments."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        # Create .gitignore with comments
        gitignore = application.base_path(".gitignore")
        gitignore.write_text("# This is a comment\n*.pyc\n# Another comment\n__pycache__/\n")

        # Refresh to reload patterns
        ignore_service = application.make(FileIgnoreService)
        await ignore_service.refresh()

        # Should still ignore .pyc files
        pyc_file = application.base_path("test.pyc")
        assert ignore_service.is_ignored(Path(pyc_file)) is True

    @pytest.mark.asyncio
    async def test_ignores_byte_cache_directory(self, application: Application):
        """Test that .byte/cache directory is ignored per config."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create path in .byte/cache
        cache_file = application.base_path(".byte/cache/file.txt")

        # Should be ignored
        assert ignore_service.is_ignored(Path(cache_file)) is True

    @pytest.mark.asyncio
    async def test_ignores_node_modules(self, application: Application):
        """Test that node_modules directory is ignored per config."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create path in node_modules
        node_file = application.base_path("node_modules/package/index.js")

        # Should be ignored
        assert ignore_service.is_ignored(Path(node_file)) is True

    @pytest.mark.asyncio
    async def test_ignores_venv_directory(self, application: Application):
        """Test that .venv directory is ignored per config."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create path in .venv
        venv_file = application.base_path(".venv/lib/python3.12/site-packages/module.py")

        # Should be ignored
        assert ignore_service.is_ignored(Path(venv_file)) is True

    @pytest.mark.asyncio
    async def test_ignores_git_directory(self, application: Application):
        """Test that .git directory is ignored per config."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # Create path in .git
        git_file = application.base_path(".git/objects/abc123")

        # Should be ignored
        assert ignore_service.is_ignored(Path(git_file)) is True

    @pytest.mark.asyncio
    async def test_handles_wildcard_patterns(self, application: Application):
        """Test that wildcard patterns work correctly."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        # Add wildcard pattern to config
        config = application["config"]
        config.files.ignore.append("*.log")

        # Refresh to pick up new pattern
        ignore_service = application.make(FileIgnoreService)
        await ignore_service.refresh()

        # Create .log file path
        log_file = application.base_path("debug.log")

        # Should be ignored
        assert ignore_service.is_ignored(Path(log_file)) is True

        # Non-log file should not be ignored
        txt_file = application.base_path("debug.txt")
        assert ignore_service.is_ignored(Path(txt_file)) is False

    @pytest.mark.asyncio
    async def test_handles_directory_patterns_with_trailing_slash(self, application: Application):
        """Test that directory patterns with trailing slash work correctly."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # __pycache__/ pattern should match directory
        pycache_dir = application.base_path("__pycache__")

        # Should be ignored
        assert ignore_service.is_ignored(Path(pycache_dir)) is True

    @pytest.mark.asyncio
    async def test_does_not_ignore_readme(self, application: Application):
        """Test that README.md is not ignored."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        ignore_service = application.make(FileIgnoreService)

        # README.md should not be ignored
        readme = application.base_path("README.md")
        assert ignore_service.is_ignored(Path(readme)) is False

    @pytest.mark.asyncio
    async def test_handles_multiple_ignore_sources(self, application: Application):
        """Test that patterns from both .gitignore and config are combined."""
        from pathlib import Path

        from byte.files import FileIgnoreService

        # Add custom pattern to config
        config = application["config"]
        config.files.ignore.append("custom_pattern.txt")

        # Refresh to combine patterns
        ignore_service = application.make(FileIgnoreService)
        await ignore_service.refresh()

        # File matching .gitignore pattern should be ignored
        pyc_file = application.base_path("test.pyc")
        assert ignore_service.is_ignored(Path(pyc_file)) is True

        # File matching config pattern should be ignored
        custom_file = application.base_path("custom_pattern.txt")
        assert ignore_service.is_ignored(Path(custom_file)) is True

        # File matching neither should not be ignored
        regular_file = application.base_path("regular.py")
        assert ignore_service.is_ignored(Path(regular_file)) is False
