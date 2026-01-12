from __future__ import annotations

from typing import TYPE_CHECKING

import git
import pytest
import pytest_asyncio
import yaml

from byte.config import ByteConfig

if TYPE_CHECKING:
    pass


class BaseTest:
    """Base test class for all Byte tests."""

    @pytest_asyncio.fixture
    async def application(self, git_repo, providers):
        """Create application with FileServiceProvider for testing."""
        from byte import Application
        from byte.foundation import Kernel

        application = Application.configure(git_repo, providers).create()

        kernel = application.make(Kernel, app=application)
        kernel.bootstrap()

        # Now we can Async boot all the providers
        await kernel.app.boot()

        return application

    @pytest.fixture
    def git_repo(self, tmp_path, config):
        """Create a temporary git repository for testing.

        Usage: Tests can use this fixture to get a Path to a git repo.
        """
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create base files
        readme = repo_path / "README.md"
        readme.write_text("# Test Project\n\nThis is a test project.\n")

        gitignore = repo_path / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n.pytest_cache/\n")

        # Create .byte directory
        byte_dir = repo_path / ".byte"
        byte_dir.mkdir()

        # Create config.yaml with test configuration
        config_data = config.model_dump(exclude_none=True, mode="json")
        config_path = byte_dir / "config.yaml"

        with open(config_path, "w") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False, sort_keys=False)

        # Create the other directories
        byte_cache_dir = repo_path / ".byte" / "cache"
        byte_cache_dir.mkdir()

        # Initial commit
        repo.index.add(["README.md", ".gitignore", ".byte/config.yaml"])
        repo.index.commit("Initial commit")

        yield repo_path
        repo.close()

    @pytest.fixture(scope="session", autouse=True)
    def set_test_environment(self):
        """Configure testing environment for all tests."""
        import os

        os.environ["BYTE_ENV"] = "testing"

    @pytest.fixture
    def config(self):
        """Create a ByteConfig instance with a temporary git repository.

        Usage: Tests can use this fixture to get a configured ByteConfig.
        """
        return ByteConfig()
