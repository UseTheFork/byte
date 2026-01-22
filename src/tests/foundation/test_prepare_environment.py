from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from byte.cli import Menu
from tests.base_test import BaseTest

if TYPE_CHECKING:
    pass


class TestPrepareEnvironment(BaseTest):
    """Test suite for PrepareEnvironment bootstrapper."""

    @pytest.fixture
    def providers(self):
        """Provide no additional providers for bootstrap tests."""
        return []

    @pytest.mark.asyncio
    async def test_first_boot_creates_config_file(
        self,
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
