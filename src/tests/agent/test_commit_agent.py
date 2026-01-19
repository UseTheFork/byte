from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from byte.git import CommitMessage, CommitPlan, CommitService
from byte.support.mixins import UserInteractive
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestCommitAgent(BaseTest):
    """Test suite for Commit Agent."""

    @pytest.fixture
    def providers(self):
        """Provide AgentServiceProvider for commit agent tests."""
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
        repo.index.add([str(test_file.relative_to(application.root_path())), "old_api.py", "new_api.py"])

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

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_commit_agent_detects_breaking_change(self, application: Application, mocker: MockerFixture):
        """Test that Commit Agent detects and marks breaking changes."""
        from byte.agent.implementations.commit.agent import CommitAgent
        from byte.git import GitService

        # Mock user confirmation to return True
        mocker.patch.object(UserInteractive, "prompt_for_confirm_or_input", return_value=(True, ""))

        # Create a file that explicitly indicates a breaking change
        breaking_content = """
        BREAKING CHANGE: This change removes the old API endpoint.
        The /api/v1/users endpoint has been removed and replaced with /api/v2/users.
        """
        test_file = await self.create_test_file(application, "api_changes.txt", breaking_content)

        # Create additional Python files to reinforce the breaking change
        old_api_content = """
def get_users():
    '''Old API endpoint - REMOVED'''
    pass
"""
        await self.create_test_file(application, "old_api.py", old_api_content)

        new_api_content = """
def get_users_v2():
    '''New API endpoint replacing /api/v1/users'''
    return {'users': []}
"""
        await self.create_test_file(application, "new_api.py", new_api_content)

        # Enable breaking changes in config
        orig_config = application["config"]
        orig_config.git.enable_breaking_changes = True
        application.instance("config", orig_config)

        commit_service = application.make(CommitService)

        git_service = application.make(GitService)
        repo = await git_service.get_repo()
        repo.index.add([str(test_file.relative_to(application.root_path()))])

        prompt = await commit_service.build_commit_prompt()

        # Create the agent
        agent = application.make(CommitAgent)

        result = await agent.execute(
            prompt,
            display_mode="silent",
        )

        application["log"].info(result["extracted_content"])

        # Verify the agent detected the breaking change
        assert "extracted_content" in result
        assert isinstance(result["extracted_content"], CommitMessage)
        assert result["extracted_content"].breaking_change == True
        assert result["extracted_content"].breaking_change_message is not None

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_commit_agent_handles_validation_rejection_and_retry(
        self, application: Application, mocker: MockerFixture
    ):
        """Test that Commit Agent handles user rejection and successfully retries with revised message."""
        from byte.agent.implementations.commit.agent import CommitAgent
        from byte.git import GitService

        # Mock user confirmation to return True
        mocker.patch.object(
            UserInteractive,
            "prompt_for_confirm_or_input",
            return_value=(False, "Change the wording of the message to be MUCH more casual."),
            side_effect=[
                (False, "Change the wording of the message to be MUCH more casual."),
                (True, ""),
            ],
        )

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

        result = await agent.execute(
            prompt,
            display_mode="silent",
        )

        # Verify the agent detected the breaking change
        assert "extracted_content" in result
        assert isinstance(result["extracted_content"], CommitMessage)
        assert result["extracted_content"].commit_message == "throw in some test files for kicks"


# f"{prompt} ** IMPORTANT: MAKE SURE TO MARK THIS COMMIT AS A BREAKING CHANGES COMMIT ** ** IMPORTANT: MAKE SURE TO MARK THIS COMMIT AS A BREAKING CHANGES COMMIT ** ** IMPORTANT: MAKE SURE TO MARK THIS COMMIT AS A BREAKING CHANGES COMMIT **",


class TestCommitPlanAgent(BaseTest):
    """Test suite for Commit Plan Agent."""

    @pytest.fixture
    def providers(self):
        """Provide AgentServiceProvider for commit agent tests."""
        from byte.agent import AgentServiceProvider
        from byte.git import GitServiceProvider

        return [AgentServiceProvider, GitServiceProvider]

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_commit_plan_agent_generates_commit_message(
        self,
        application: Application,
    ):
        """Test that Commit Plan Agent generates a structured commit message."""
        from byte.agent.implementations.commit.agent import CommitPlanAgent
        from byte.git import GitService

        # Create and stage a test file
        test_file = await self.create_test_file(application, "test_commit.txt", "test content")

        commit_service = application.make(CommitService)

        git_service = application.make(GitService)
        repo = await git_service.get_repo()
        repo.index.add([str(test_file.relative_to(application.root_path()))])

        prompt = await commit_service.build_commit_prompt()

        # Create the agent
        agent = application.make(CommitPlanAgent)

        result = await agent.execute(prompt, display_mode="silent")

        application["log"].info(result["extracted_content"])

        # Verify the agent generated a commit plan
        assert "extracted_content" in result
        assert isinstance(result["extracted_content"], CommitPlan)
        assert len(result["extracted_content"].commits) == 1

        commit_group = result["extracted_content"].commits[0]
        assert commit_group.type == "chore"
        assert commit_group.commit_message == "add initial test commit file"
        assert commit_group.breaking_change == False
        assert commit_group.scope is None
        assert commit_group.files == ["test_commit.txt"]
