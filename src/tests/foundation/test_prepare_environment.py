"""Test suite for PrepareEnvironment bootstrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from byte.cli import Menu

if TYPE_CHECKING:
    pass


@pytest.fixture
def providers():
    """Provide no additional providers for bootstrap tests."""
    return []


@pytest.mark.asyncio
async def test_first_boot_creates_config_file(
    tmp_path,
    config,
    mocker: MockerFixture,
):
    """Test that first boot creates config.yaml file."""
    import git
    import yaml

    from byte import Application
    from byte.foundation.bootstrap import PrepareEnvironment

    # Create a fresh git repo without config
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)

    mocker.patch.object(Menu, "confirm", return_value=True)
    mocker.patch.object(Menu, "select", return_value="anthropic")

    # Create minimal app
    app = Application(base_path=repo_path)
    app.instance("args", {"flags": [], "options": {}})

    # Run bootstrap
    bootstrapper = PrepareEnvironment()
    bootstrapper.bootstrap(app)

    # Verify config.yaml was created
    config_path = app.config_path("config.yaml")
    assert config_path.exists()

    # Verify it contains valid YAML
    with open(config_path) as f:
        config_data = yaml.safe_load(f)
    assert config_data is not None
    assert "llm" in config_data

    repo.close()


@pytest.mark.asyncio
async def test_subsequent_boot_skips_first_boot_setup(
    tmp_path,
    config,
    mocker: MockerFixture,
):
    """Test that subsequent boots skip first boot setup when config exists."""
    import git
    import yaml

    from byte import Application
    from byte.foundation.bootstrap import PrepareEnvironment

    # Create a git repo with existing config
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)

    # Create .byte directory and config.yaml
    byte_dir = repo_path / ".byte"
    byte_dir.mkdir()
    config_path = byte_dir / "config.yaml"

    config_data = config.model_dump(exclude_none=True, mode="json")
    with open(config_path, "w") as f:
        yaml.safe_dump(config_data, f, default_flow_style=False, sort_keys=False)

    # Create minimal app
    app = Application(base_path=repo_path)
    app.instance("args", {"flags": [], "options": {}})

    # Spy on _run_first_boot_setup to verify it's NOT called
    bootstrapper = PrepareEnvironment()
    spy = mocker.spy(bootstrapper, "_run_first_boot_setup")

    # Run bootstrap
    bootstrapper.bootstrap(app)

    # Verify _run_first_boot_setup was NOT called
    spy.assert_not_called()

    repo.close()
