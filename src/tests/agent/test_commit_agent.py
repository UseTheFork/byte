from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from byte.git import CommitMessage, CommitService
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestCommitAgent(BaseTest):
    """Test suite for Commit Agent."""

    @pytest.fixture
    def providers(self):
        """Provide AgentServiceProvider for commit agent tests."""
        from byte.agent import AgentServiceProvider
        from byte.git import GitServiceProvider

        return [AgentServiceProvider, GitServiceProvider]

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_commit_agent_generates_commit_message(
        self,
        application: Application,
    ):
        """Test that Commit Agent generates a structured commit message."""
        from byte.agent.implementations.commit.agent import CommitAgent
        from byte.git import GitService

        # Create and stage a test file
        test_file = await self.create_test_file(application, "test_commit.txt", "test content")

        commit_service = application.make(CommitService)

        git_service = application.make(GitService)
        repo = await git_service.get_repo()
        repo.index.add([str(test_file.relative_to(application.root_path()))])

        prompt = await commit_service.build_commit_prompt()

        # Create the agent
        agent = application.make(CommitAgent)

        result = await agent.execute(prompt, display_mode="silent")

        # Verify the agent generated a commit message
        assert "extracted_content" in result
        assert isinstance(result["extracted_content"], CommitMessage)
        assert result["extracted_content"].type == "feat"
        assert result["extracted_content"].commit_message == "add test commit file"
        assert result["extracted_content"].breaking_change == False
        assert result["extracted_content"].scope is None

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_commit_agent_generates_commit_message_with_multiple_files(self, application: Application):
        """Test that Commit Agent generates a commit message for multiple file changes."""
        from byte.agent.implementations.commit.agent import CommitAgent
        from byte.git import GitService

        # Create and stage two test files
        test_file1 = await self.create_test_file(application, "test_commit_1.txt", "first test content")
        test_file2 = await self.create_test_file(application, "test_commit_2.txt", "second test content")

        commit_service = application.make(CommitService)

        git_service = application.make(GitService)
        repo = await git_service.get_repo()
        repo.index.add(
            [str(test_file1.relative_to(application.root_path())), str(test_file2.relative_to(application.root_path()))]
        )

        prompt = await commit_service.build_commit_prompt()

        # Create the agent
        agent = application.make(CommitAgent)

        result = await agent.execute(prompt, display_mode="silent")

        # application["log"].info(result["extracted_content"])

        # Verify the agent generated a commit message
        assert "extracted_content" in result
        assert isinstance(result["extracted_content"], CommitMessage)
        assert result["extracted_content"].type == "feat"
        assert result["extracted_content"].commit_message == "add initial test commit files"
        assert result["extracted_content"].breaking_change == False
        assert result["extracted_content"].scope is None
