"""Test suite for Commit Plan Agent."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from byte.git import CommitPlan, CommitService
from byte.support.mixins import UserInteractive
from tests.utils import create_test_file

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide AgentServiceProvider for commit agent tests."""
    from byte.agent import AgentServiceProvider
    from byte.git import GitServiceProvider

    return [AgentServiceProvider, GitServiceProvider]


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_commit_plan_agent_generates_commit_message(
    application: Application,
    mocker: MockerFixture,
):
    """Test that Commit Plan Agent generates a structured commit message."""
    from byte.agent.implementations.commit.agent import CommitPlanAgent
    from byte.git import GitService

    # Mock user confirmation to return True
    mocker.patch.object(
        UserInteractive,
        "prompt_for_confirmation",
        return_value=True,
    )

    # Create and stage a test file
    test_file = await create_test_file(application, "test_commit.txt", "test content")

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


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_commit_plan_agent_generates_separate_commits_for_multiple_files(
    application: Application,
    mocker: MockerFixture,
):
    """Test that Commit Plan Agent generates separate commits for multiple files."""
    from byte.agent.implementations.commit.agent import CommitPlanAgent
    from byte.git import GitService

    # Mock user confirmation to return True
    mocker.patch.object(
        UserInteractive,
        "prompt_for_confirmation",
        return_value=True,
    )

    # Create and stage two test files
    test_file1 = await create_test_file(application, "test_commit_1.txt", "first test content")
    test_file2 = await create_test_file(application, "test_commit_2.txt", "second test content")

    commit_service = application.make(CommitService)

    git_service = application.make(GitService)
    repo = await git_service.get_repo()
    repo.index.add(
        [str(test_file1.relative_to(application.root_path())), str(test_file2.relative_to(application.root_path()))]
    )

    prompt = await commit_service.build_commit_prompt()

    # Create the agent
    agent = application.make(CommitPlanAgent)

    result = await agent.execute(
        prompt,
        display_mode="silent",
    )

    # Verify the agent generated a commit plan with two separate commits
    assert "extracted_content" in result
    assert isinstance(result["extracted_content"], CommitPlan)
    assert len(result["extracted_content"].commits) == 2

    # Verify first commit
    commit1 = result["extracted_content"].commits[0]
    assert commit1.type == "chore"
    assert commit1.scope is None
    assert commit1.commit_message == "add test_commit_1.txt"
    assert commit1.breaking_change == False
    assert commit1.breaking_change_message is None
    assert commit1.body is None
    assert commit1.files == ["test_commit_1.txt"]

    # Verify second commit
    commit2 = result["extracted_content"].commits[1]
    assert commit2.type == "chore"
    assert commit2.scope is None
    assert commit2.commit_message == "add test_commit_2.txt"
    assert commit2.breaking_change == False
    assert commit2.breaking_change_message is None
    assert commit2.body is None
    assert commit2.files == ["test_commit_2.txt"]


# f"{prompt} ** IMPORTANT: MAKE SURE TO MARK THIS COMMIT AS A BREAKING CHANGES COMMIT ** ** IMPORTANT: MAKE SURE TO MARK THIS COMMIT AS A BREAKING CHANGES COMMIT ** ** IMPORTANT: MAKE SURE TO MARK THIS COMMIT AS A BREAKING CHANGES COMMIT **",
