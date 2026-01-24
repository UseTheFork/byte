"""Test suite for config migrations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import yaml

from byte.config.migrator import Migrator

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def git_repo_v0(tmp_path):
    """Create a temporary git repository with v0 config for testing migrations.

    Usage: Tests can use this fixture to get a Path to a git repo with old config.
    """
    import git

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

    # Create v0 config.yaml with old structure
    config_data = {
        "version": "0.0.0",
        "llm": {
            "model": "claude-sonnet-4-5",
        },
    }
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


@pytest.fixture
def providers():
    """Provide empty providers list for migration tests."""
    return []


@pytest.mark.asyncio
async def test_migration_001_migrates_model_to_main_and_weak(git_repo_v0: Path, providers):
    """Test that migration 001 migrates llm.model to main_model and weak_model."""
    from byte import Application
    from byte.foundation import Kernel

    application = Application.configure(git_repo_v0, providers).create()
    application.make(Kernel, app=application)

    # Load the old config
    config_path = git_repo_v0 / ".byte" / "config.yaml"
    with open(config_path) as f:
        config_dict = yaml.safe_load(f)

    # Verify old structure
    assert config_dict["version"] == "0.0.0"
    assert config_dict["llm"]["model"] == "claude-sonnet-4-5"
    assert "main_model" not in config_dict["llm"]
    assert "weak_model" not in config_dict["llm"]

    # Run migration
    migrator = Migrator(application)
    migrated_config = migrator.handle(config_dict)

    # Verify new structure
    assert migrated_config["version"] == "1.0.0"
    assert "model" not in migrated_config["llm"]
    assert migrated_config["llm"]["main_model"]["model"] == "claude-sonnet-4-5"
    assert migrated_config["llm"]["main_model"]["weak_model"] == "claude-sonnet-4-5"


@pytest.mark.asyncio
async def test_migration_skips_when_version_matches(git_repo: Path, providers):
    """Test that migration is skipped when config version matches target."""
    from byte import Application
    from byte.foundation import Kernel

    application = Application.configure(git_repo, providers).create()
    application.make(Kernel, app=application)

    # Load current config
    config_path = git_repo / ".byte" / "config.yaml"
    with open(config_path) as f:
        config_dict = yaml.safe_load(f)

    original_version = config_dict.get("version", "0.0.0")

    # Run migration
    migrator = Migrator(application)
    migrated_config = migrator.handle(config_dict)

    # Version should remain unchanged
    assert migrated_config["version"] == original_version


@pytest.mark.asyncio
async def test_migration_handles_missing_llm_section(git_repo_v0: Path, providers):
    """Test that migration handles config without llm section."""
    from byte import Application
    from byte.foundation import Kernel

    application = Application.configure(git_repo_v0, providers).create()
    application.make(Kernel, app=application)

    # Create config without llm section
    config_dict = {"version": "0.0.0"}

    # Run migration
    migrator = Migrator(application)
    migrated_config = migrator.handle(config_dict)

    # Should create llm section
    assert "llm" in migrated_config
    assert migrated_config["version"] == "1.0.0"
