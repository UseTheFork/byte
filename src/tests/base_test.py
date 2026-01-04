import git
import pytest
import pytest_asyncio

from byte import Container
from byte.core import ByteConfig
from tests.container_factory import TestContainerFactory


class BaseTest:
    """Base test class for all Byte tests."""

    @pytest.fixture
    def git_repo(self, tmp_path):
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

        # Initial commit
        repo.index.add(["README.md", ".gitignore"])
        repo.index.commit("Initial commit")

        yield repo_path
        repo.close()

    @pytest.fixture
    def test_config(self, git_repo):
        """Create a ByteConfig instance with a temporary git repository.

        Usage: Tests can use this fixture to get a configured ByteConfig.
        """
        return ByteConfig(project_root=git_repo)

    @pytest_asyncio.fixture
    async def container(self, test_config: ByteConfig) -> Container:
        """Create container with SessionContextService and dependencies."""
        container = await TestContainerFactory.create_minimal(test_config)
        return container
