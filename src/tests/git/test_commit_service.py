"""Test suite for CommitService."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from byte.git import CommitGroup, CommitMessage, CommitPlan
from tests.utils import create_test_file

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide GitServiceProvider for commit service tests."""
    from byte.git import GitServiceProvider

    return [GitServiceProvider]


@pytest.mark.asyncio
async def test_build_commit_prompt_returns_formatted_prompt(application: Application):
    """Test that build_commit_prompt returns a formatted prompt string."""
    from byte.git import CommitService, GitService

    # Create and stage a file
    test_file = await create_test_file(application, "prompt_test.txt", "test content")

    git_service = application.make(GitService)
    repo = await git_service.get_repo()
    repo.index.add([str(test_file.relative_to(application.root_path()))])

    service = application.make(CommitService)
    prompt = await service.build_commit_prompt()

    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "prompt_test.txt" in prompt


@pytest.mark.asyncio
async def test_build_commit_prompt_includes_diff_content(application: Application):
    """Test that build_commit_prompt includes diff content for modified files."""
    from byte.git import CommitService, GitService

    # Create, commit, then modify a file
    test_file = await create_test_file(application, "diff_prompt_test.txt", "original content")

    git_service = application.make(GitService)
    repo = await git_service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file")

    # Modify and stage
    test_file.write_text("modified content")
    repo.index.add([file_path])

    service = application.make(CommitService)
    prompt = await service.build_commit_prompt()

    assert "diff_prompt_test.txt" in prompt
    assert "modified" in prompt.lower()


@pytest.mark.asyncio
async def test_format_conventional_commit_basic_message(application: Application):
    """Test that format_conventional_commit formats a basic commit message."""
    from byte.git import CommitService

    commit_message = CommitMessage(
        type="feat",
        scope=None,
        commit_message="Add new feature",
        breaking_change=False,
    )

    service = application.make(CommitService)
    formatted = await service.format_conventional_commit(commit_message)

    assert formatted == "feat: add new feature"


@pytest.mark.asyncio
async def test_format_conventional_commit_with_scope(application: Application, config):
    """Test that format_conventional_commit includes scope when enabled."""
    from byte.git import CommitService

    # Enable scopes in config
    config.git.enable_scopes = True
    application.instance("config", config)

    commit_message = CommitMessage(
        type="feat",
        scope="api",
        commit_message="Add new endpoint",
        breaking_change=False,
    )

    service = application.make(CommitService)
    formatted = await service.format_conventional_commit(commit_message)

    assert formatted == "feat(api): add new endpoint"


@pytest.mark.asyncio
async def test_format_conventional_commit_without_scope_when_disabled(application: Application, config):
    """Test that format_conventional_commit excludes scope when disabled in config."""
    from byte.git import CommitService

    # Disable scopes in config
    config.git.enable_scopes = False
    application.instance("config", config)

    commit_message = CommitMessage(
        type="feat",
        scope="api",
        commit_message="Add new endpoint",
        breaking_change=False,
    )

    service = application.make(CommitService)
    formatted = await service.format_conventional_commit(commit_message)

    assert formatted == "feat: add new endpoint"
    assert "(api)" not in formatted


@pytest.mark.asyncio
async def test_format_conventional_commit_with_body(application: Application, config):
    """Test that format_conventional_commit includes body when enabled."""
    from byte.git import CommitService

    # Enable body in config
    config.git.enable_body = True
    application.instance("config", config)

    commit_message = CommitMessage(
        type="feat",
        scope=None,
        commit_message="Add new feature",
        breaking_change=False,
        body="This feature adds support for new functionality.",
    )

    service = application.make(CommitService)
    formatted = await service.format_conventional_commit(commit_message)

    assert "feat: add new feature" in formatted
    assert "This feature adds support for new functionality." in formatted


@pytest.mark.asyncio
async def test_format_conventional_commit_without_body_when_disabled(application: Application, config):
    """Test that format_conventional_commit excludes body when disabled in config."""
    from byte.git import CommitService

    # Disable body in config
    config.git.enable_body = False
    application.instance("config", config)

    commit_message = CommitMessage(
        type="feat",
        scope=None,
        commit_message="Add new feature",
        breaking_change=False,
        body="This should not appear.",
    )

    service = application.make(CommitService)
    formatted = await service.format_conventional_commit(commit_message)

    assert formatted == "feat: add new feature"
    assert "This should not appear." not in formatted


@pytest.mark.asyncio
async def test_format_conventional_commit_normalizes_description(application: Application):
    """Test that format_conventional_commit normalizes the description."""
    from byte.git import CommitService

    commit_message = CommitMessage(
        type="feat",
        scope=None,
        commit_message="Add new feature.",
        breaking_change=False,
    )

    service = application.make(CommitService)
    formatted = await service.format_conventional_commit(commit_message)

    # Should lowercase first char and remove trailing period
    assert formatted == "feat: add new feature"


@pytest.mark.asyncio
async def test_format_conventional_commit_breaking_change_confirmed(application: Application, config, mocker):
    """Test that format_conventional_commit handles confirmed breaking changes."""
    from byte.git import CommitService

    # Enable breaking changes in config
    config.git.enable_breaking_changes = True
    application.instance("config", config)

    commit_message = CommitMessage(
        type="feat",
        scope=None,
        commit_message="Change API signature",
        breaking_change=True,
        breaking_change_message="The API now requires authentication.",
    )

    service = application.make(CommitService)

    # Mock user confirmation to return True
    mocker.patch.object(service, "prompt_for_confirmation", return_value=True)

    formatted = await service.format_conventional_commit(commit_message)

    assert "feat!: change API signature" in formatted
    assert "BREAKING CHANGE: The API now requires authentication." in formatted


@pytest.mark.asyncio
async def test_format_conventional_commit_breaking_change_declined(application: Application, config, mocker):
    """Test that format_conventional_commit handles declined breaking changes."""
    from byte.git import CommitService

    # Enable breaking changes in config
    config.git.enable_breaking_changes = True
    application.instance("config", config)

    commit_message = CommitMessage(
        type="feat",
        scope=None,
        commit_message="Change API signature",
        breaking_change=True,
        breaking_change_message="The API now requires authentication.",
    )

    service = application.make(CommitService)

    # Mock user confirmation to return False
    mocker.patch.object(service, "prompt_for_confirmation", return_value=False)

    formatted = await service.format_conventional_commit(commit_message)

    # Should not include breaking change marker or footer
    assert formatted == "feat: change API signature"
    assert "!" not in formatted
    assert "BREAKING CHANGE" not in formatted


@pytest.mark.asyncio
async def test_format_conventional_commit_breaking_change_disabled(application: Application, config):
    """Test that format_conventional_commit ignores breaking changes when disabled."""
    from byte.git import CommitService

    # Disable breaking changes in config
    config.git.enable_breaking_changes = False
    application.instance("config", config)

    commit_message = CommitMessage(
        type="feat",
        scope=None,
        commit_message="Change API signature",
        breaking_change=True,
        breaking_change_message="The API now requires authentication.",
    )

    service = application.make(CommitService)
    formatted = await service.format_conventional_commit(commit_message)

    # Should not prompt or include breaking change markers
    assert formatted == "feat: change API signature"
    assert "!" not in formatted
    assert "BREAKING CHANGE" not in formatted


@pytest.mark.asyncio
async def test_process_commit_plan_creates_multiple_commits(application: Application):
    """Test that process_commit_plan creates separate commits for each group."""
    from byte.git import CommitService, GitService

    # Create multiple files
    file1 = await create_test_file(application, "plan_test1.txt", "content 1")
    file2 = await create_test_file(application, "plan_test2.txt", "content 2")

    git_service = application.make(GitService)
    repo = await git_service.get_repo()
    repo.index.add(
        [
            str(file1.relative_to(application.root_path())),
            str(file2.relative_to(application.root_path())),
        ]
    )

    # Create commit plan with two groups
    commit_plan = CommitPlan(
        commits=[
            CommitGroup(
                type="feat",
                scope=None,
                commit_message="Add first file",
                breaking_change=False,
                files=["plan_test1.txt"],
            ),
            CommitGroup(
                type="feat",
                scope=None,
                commit_message="Add second file",
                breaking_change=False,
                files=["plan_test2.txt"],
            ),
        ]
    )

    service = application.make(CommitService)
    await service.process_commit_plan(commit_plan)

    # Verify two commits were created
    commits = list(repo.iter_commits(max_count=2))
    assert len(commits) == 2
    assert "add first file" in commits[1].message
    assert "add second file" in commits[0].message


@pytest.mark.asyncio
async def test_process_commit_plan_handles_deleted_files(application: Application):
    """Test that process_commit_plan handles deleted files correctly."""
    from byte.git import CommitService, GitService

    # Create and commit a file
    test_file = await create_test_file(application, "delete_plan_test.txt", "content to delete")

    git_service = application.make(GitService)
    repo = await git_service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file to delete")

    # Delete and stage the file
    test_file.unlink()
    repo.index.remove([file_path])

    # Create commit plan for deletion
    commit_plan = CommitPlan(
        commits=[
            CommitGroup(
                type="chore",
                scope=None,
                commit_message="Remove obsolete file",
                breaking_change=False,
                files=["delete_plan_test.txt"],
            ),
        ]
    )

    service = application.make(CommitService)
    await service.process_commit_plan(commit_plan)

    # Verify commit was created
    latest_commit = repo.head.commit
    assert "remove obsolete file" in latest_commit.message


@pytest.mark.asyncio
async def test_generate_commit_guidelines_includes_commit_types(application: Application):
    """Test that generate_commit_guidelines includes all commit types."""
    from byte.git import CommitService

    service = application.make(CommitService)
    guidelines = await service.generate_commit_guidelines()

    assert "feat" in guidelines
    assert "fix" in guidelines
    assert "refactor" in guidelines
    assert "docs" in guidelines


@pytest.mark.asyncio
async def test_generate_commit_guidelines_includes_description_rules(application: Application):
    """Test that generate_commit_guidelines includes description formatting rules."""
    from byte.git import CommitService

    service = application.make(CommitService)
    guidelines = await service.generate_commit_guidelines()

    assert "imperative mood" in guidelines.lower()
    assert "lowercase" in guidelines.lower()


@pytest.mark.asyncio
async def test_generate_commit_guidelines_includes_scopes_when_enabled(application: Application, config):
    """Test that generate_commit_guidelines includes scopes when enabled."""
    from byte.git import CommitService

    # Enable scopes in config
    config.git.enable_scopes = True
    config.git.scopes = ["api", "ui", "core"]
    application.instance("config", config)

    service = application.make(CommitService)
    guidelines = await service.generate_commit_guidelines()

    assert "api" in guidelines
    assert "ui" in guidelines
    assert "core" in guidelines


@pytest.mark.asyncio
async def test_generate_commit_guidelines_excludes_scope_when_disabled(application: Application, config):
    """Test that generate_commit_guidelines indicates scope exclusion when disabled."""
    from byte.git import CommitService

    # Disable scopes in config
    config.git.enable_scopes = False
    application.instance("config", config)

    service = application.make(CommitService)
    guidelines = await service.generate_commit_guidelines()

    assert "DO NOT include `scope`" in guidelines


@pytest.mark.asyncio
async def test_generate_commit_guidelines_excludes_body_when_disabled(application: Application, config):
    """Test that generate_commit_guidelines indicates body exclusion when disabled."""
    from byte.git import CommitService

    # Disable body in config
    config.git.enable_body = False
    application.instance("config", config)

    service = application.make(CommitService)
    guidelines = await service.generate_commit_guidelines()

    assert "DO NOT include `body`" in guidelines


@pytest.mark.asyncio
async def test_generate_commit_guidelines_excludes_breaking_changes_when_disabled(application: Application, config):
    """Test that generate_commit_guidelines indicates breaking change exclusion when disabled."""
    from byte.git import CommitService

    # Disable breaking changes in config
    config.git.enable_breaking_changes = False
    application.instance("config", config)

    service = application.make(CommitService)
    guidelines = await service.generate_commit_guidelines()

    assert "DO NOT include `breaking_change`" in guidelines


@pytest.mark.asyncio
async def test_generate_commit_guidelines_includes_custom_description_guidelines(application: Application, config):
    """Test that generate_commit_guidelines includes custom description guidelines from config."""
    from byte.git import CommitService

    # Add custom guidelines
    config.git.description_guidelines = ["Use ticket numbers", "Reference pull requests"]
    application.instance("config", config)

    service = application.make(CommitService)
    guidelines = await service.generate_commit_guidelines()

    assert "Use ticket numbers" in guidelines
    assert "Reference pull requests" in guidelines
