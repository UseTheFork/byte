from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from byte.files import FileMode, FileService
from byte.support.mixins import UserInteractive
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestCoderAgentPHP(BaseTest):
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
        request = "Create a new file called hello.php with a simple hello world function"

        await agent.execute(request, display_mode="silent")

        # Verify the agent created the file
        hello_file = application.root_path("hello.php")
        assert hello_file.exists()

        content = hello_file.read_text()
        assert "function" in content
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
        initial_content = """<?php
function greet($name) {
    return "Hello, $name";
}
"""
        test_file = await self.create_test_file(application, "greet.php", initial_content)
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
        assert "function greet($name)" in content

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_coder_agent_deletes_file(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that Coder Agent can delete an existing file."""
        from byte.agent.implementations.coder.agent import CoderAgent

        mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

        # Create a test file
        test_content = """<?php
function temporary_function() {
    // Empty function
}
"""
        test_file = await self.create_test_file(application, "temp.php", test_content)

        # Add file to file service
        file_service = application.make(FileService)
        await file_service.add_file(test_file, FileMode.EDITABLE)

        # Verify file exists
        assert test_file.exists()

        # Create the agent
        agent = application.make(CoderAgent)

        # Request to delete the file
        request = "Delete the temp.php file"

        await agent.execute(request, display_mode="silent")

        # Verify the file was deleted
        assert not test_file.exists()

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_coder_agent_creates_multiple_files(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that Coder Agent can create multiple files in a single request."""
        from byte.agent.implementations.coder.agent import CoderAgent

        mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

        # Create the agent
        agent = application.make(CoderAgent)

        # Request to create two files
        request = "Create two files: utils.php with a helper function and config.php with a settings array"

        await agent.execute(request, display_mode="silent")

        # Verify both files were created
        utils_file = application.root_path("utils.php")
        config_file = application.root_path("config.php")

        assert utils_file.exists()
        assert config_file.exists()

        # Verify utils.php has a function
        utils_content = utils_file.read_text()
        assert "function" in utils_content
        assert not utils_content.startswith("\n"), "File should not start with a blank line"

        # Verify config.php has an array
        config_content = config_file.read_text()
        assert "array" in config_content.lower() or "[" in config_content
        assert not config_content.startswith("\n"), "File should not start with a blank line"

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_coder_agent_creates_edits_and_deletes_files(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that Coder Agent can create, edit, and delete files in a single request."""
        from byte.agent.implementations.coder.agent import CoderAgent

        mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

        # Create an existing file to edit
        existing_content = """<?php
function calculate($a, $b) {
    return $a + $b;
}
"""
        existing_file = await self.create_test_file(application, "calculator.php", existing_content)

        # Create a file to delete
        delete_content = """<?php
function old_function() {
    // Empty function
}
"""
        delete_file = await self.create_test_file(application, "old_code.php", delete_content)

        # Add both files to file service
        file_service = application.make(FileService)
        await file_service.add_file(existing_file, FileMode.EDITABLE)
        await file_service.add_file(delete_file, FileMode.EDITABLE)

        # Verify initial state
        assert existing_file.exists()
        assert delete_file.exists()

        # Create the agent
        agent = application.make(CoderAgent)

        # Request to create a new file, edit existing file, and delete old file
        request = """Do three things:
1. Create a new file called main.php with a main function that calls calculate
2. Edit calculator.php to change the function to multiply instead of add
3. Delete the old_code.php file as it's no longer needed"""

        await agent.execute(request, display_mode="silent")

        # Verify new file was created
        main_file = application.root_path("main.php")
        assert main_file.exists()
        main_content = main_file.read_text()
        assert "function main" in main_content
        assert "calculate" in main_content
        assert not main_content.startswith("\n"), "File should not start with a blank line"

        # Verify existing file was edited
        assert existing_file.exists()
        edited_content = existing_file.read_text()
        assert "function calculate($a, $b)" in edited_content
        assert "*" in edited_content or "multiply" in edited_content.lower()
        assert "+" not in edited_content or "add" not in edited_content.lower()

        # Verify old file was deleted
        assert not delete_file.exists()
