from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from byte.agent import ConventionAgent
from byte.agent.implementations.conventions.constants import FOCUS_MESSAGES
from byte.support.mixins import UserInteractive
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestConventionAgent(BaseTest):
    """Test suite for Convention Agent."""

    @pytest.fixture
    def providers(self):
        """Provide service providers for convention agent tests."""

        from byte.agent import AgentServiceProvider
        from byte.files import FileServiceProvider
        from byte.git import GitServiceProvider

        return [
            AgentServiceProvider,
            FileServiceProvider,
            GitServiceProvider,
        ]

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_convention_agent_analyzes_comment_standards(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that Convention Agent analyzes comment standards across multiple file types."""
        from byte.files import FileMode, FileService

        mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

        focus = FOCUS_MESSAGES.get("Comment Standards")

        # Create test files with various comment styles
        python_content = """def calculate(a, b):
    # This is a comment
    return a + b

class MyClass:
    '''This is a docstring'''
    pass
"""
        await self.create_test_file(application, "example.py", python_content)

        javascript_content = """// This is a single-line comment
function greet(name) {
    /* This is a
       multi-line comment */
    return `Hello, ${name}`;
}
"""
        await self.create_test_file(application, "example.js", javascript_content)

        # Add files to file service as read-only
        file_service = application.make(FileService)
        await file_service.add_file(application.root_path("example.py"), FileMode.READ_ONLY)
        await file_service.add_file(application.root_path("example.js"), FileMode.READ_ONLY)

        # Create the agent
        agent = application.make(ConventionAgent)

        result = await agent.execute(focus.focus_message, display_mode="silent")

        # Verify the agent extracted content
        assert "extracted_content" in result
        assert result["extracted_content"] is not None
        assert len(result["extracted_content"]) > 0
        assert "Comment Standards Convention" in result["extracted_content"]
        assert "JavaScript" in result["extracted_content"]
        assert "Python" in result["extracted_content"]
