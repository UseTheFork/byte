from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from byte.files import FileMode, FileService
from byte.support.mixins import UserInteractive
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestCoderAgent(BaseTest):
    """Test suite for Coder Agent."""

    @pytest.fixture
    def providers(self):
        """Provide service providers for coder agent tests."""
        from byte.agent import AgentServiceProvider
        from byte.files import FileServiceProvider

        return [
            AgentServiceProvider,
            FileServiceProvider,
        ]

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_coder_agent_creates_new_file(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that Coder Agent can create a new file with specified content."""
        from byte.agent.implementations.coder.agent import CoderAgent

        mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

        # Create the agent
        agent = application.make(CoderAgent)

        # Request to create a new file
        request = "Create a new file called hello.py with a simple hello world function"

        await agent.execute(request, display_mode="silent")

        # Verify the agent created the file
        hello_file = application.root_path("hello.py")
        assert hello_file.exists()

        content = hello_file.read_text()
        assert "def" in content
        assert "hello" in content.lower()
        assert not content.startswith("\n"), "File should not start with a blank line"

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_coder_agent_edits_existing_file(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that Coder Agent can edit an existing file."""
        from byte.agent.implementations.coder.agent import CoderAgent

        mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

        # Create a test file with initial content
        initial_content = """def greet(name):
    return f"Hello, {name}"
"""
        test_file = await self.create_test_file(application, "greet.py", initial_content)
        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Create the agent
        agent = application.make(CoderAgent)

        # Request to edit the file
        request = "Change the greet function to return 'Hi' instead of 'Hello'"

        await agent.execute(request, display_mode="silent")

        # Verify the file was edited
        assert test_file.exists()
        content = test_file.read_text()
        assert "Hi" in content
        assert "Hello" not in content
        assert "def greet(name):" in content
