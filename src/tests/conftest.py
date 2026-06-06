import json
import sys
from pathlib import Path

import git
import pytest
import pytest_asyncio

from byte.config import ByteUserConfig


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": [
            ("authorization", "XXXX"),
            ("x-api-key", "XXXX"),
        ],
        "filter_query_parameters": [
            ("api_key", "XXXX"),
            ("key", "XXXX"),
        ],
    }


@pytest_asyncio.fixture
async def application(git_repo, providers):
    """Create application with FileServiceProvider for testing."""
    from byte import Application
    from byte.foundation import Kernel

    application = Application.configure(git_repo, providers).create()

    kernel = application.make(Kernel, app=application)
    kernel.bootstrap()

    # Now we can Async boot all the providers
    await kernel.app.boot()

    # we add a new logger here for pytest
    application["log"].add(sys.stdout, colorize=True)

    return application


@pytest.fixture
def git_repo(tmp_path: Path, config: ByteUserConfig):
    """Create a temporary git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)

    # Create base files
    readme = repo_path / "README.md"
    readme.write_text("# Test Project\n\nThis is a test project.\n")

    gitignore = repo_path / ".gitignore"
    base_patterns = ["*.pyc", "__pycache__", ".pytest_cache"]
    gitignore.write_text("\n".join(base_patterns) + "\n")

    # Create .byte directory
    byte_dir = repo_path / ".byte"
    byte_dir.mkdir()

    byte_gitignore = byte_dir / ".gitignore"
    byte_patterns = ["cache/*", "session_context/*"]
    byte_gitignore.write_text("\n".join(byte_patterns) + "\n")

    # Create config.yaml with test configuration
    config_data = config.model_dump(exclude_none=True, mode="json")

    config_data = {
        "$schema": "https://raw.githubusercontent.com/UseTheFork/byte/refs/heads/main/schema.json",
        **config_data,
    }

    config_path = byte_dir / "config.jsonc"

    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)

    # Create the other directories
    byte_cache_dir = repo_path / ".byte" / "cache"
    byte_cache_dir.mkdir()

    # Initial commit
    repo.index.add(
        [
            "README.md",
            ".gitignore",
            ".byte/.gitignore",
            ".byte/config.jsonc",
        ]
    )
    repo.index.commit("Initial commit")

    yield repo_path
    repo.close()


@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    """Configure testing environment for all tests."""
    import os

    os.environ["BYTE_ENV"] = "testing"


@pytest.fixture
def config():
    """Create a ByteConfig instance with a temporary git repository."""
    config = ByteUserConfig()

    # Change the default port as byte is usually running at the same time.
    config.gateway.port = 9735

    return config
