from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestGitService(BaseTest):
    """Test suite for GitService."""

    @pytest.fixture
    def providers(self):
        """Provide GitServiceProvider for git service tests."""
        from byte.git import GitServiceProvider

        return [GitServiceProvider]

    @pytest.mark.asyncio
    async def test_get_repo_returns_repository_instance(self, application: Application):
        """Test that get_repo returns a valid git repository instance."""
        from byte.git import GitService

        service = application.make(GitService)
        repo = await service.get_repo()

        assert repo is not None
        assert hasattr(repo, "index")
        assert hasattr(repo, "git")

    @pytest.mark.asyncio
    async def test_get_changed_files_returns_modified_files(self, application: Application):
        """Test that get_changed_files returns list of modified files."""
        from byte.git import GitService

        # Create and modify a file
        test_file = await self.create_test_file(application, "test_modified.txt", "original content")

        repo = await application.make(GitService).get_repo()
        repo.index.add([str(test_file.relative_to(application.root_path()))])
        repo.index.commit("Add test file")

        # Modify the file
        test_file.write_text("modified content")

        service = application.make(GitService)
        changed_files = await service.get_changed_files()

        assert len(changed_files) > 0
        assert any(f.name == "test_modified.txt" for f in changed_files)

    @pytest.mark.asyncio
    async def test_get_changed_files_includes_untracked_by_default(self, application: Application):
        """Test that get_changed_files includes untracked files by default."""
        from byte.git import GitService

        # Create an untracked file
        await self.create_test_file(application, "untracked.txt", "untracked content")

        service = application.make(GitService)
        changed_files = await service.get_changed_files()

        assert any(f.name == "untracked.txt" for f in changed_files)

    @pytest.mark.asyncio
    async def test_get_changed_files_excludes_untracked_when_disabled(self, application: Application):
        """Test that get_changed_files excludes untracked files when include_untracked=False."""
        from byte.git import GitService

        # Create an untracked file
        await self.create_test_file(application, "untracked2.txt", "untracked content")

        service = application.make(GitService)
        changed_files = await service.get_changed_files(include_untracked=False)

        assert not any(f.name == "untracked2.txt" for f in changed_files)

    @pytest.mark.asyncio
    async def test_get_changed_files_includes_staged_files(self, application: Application):
        """Test that get_changed_files includes staged files."""
        from byte.git import GitService

        # Create and stage a file
        staged_file = await self.create_test_file(application, "staged.txt", "staged content")

        repo = await application.make(GitService).get_repo()
        repo.index.add([str(staged_file.relative_to(application.root_path()))])

        service = application.make(GitService)
        changed_files = await service.get_changed_files()

        assert any(f.name == "staged.txt" for f in changed_files)

    @pytest.mark.asyncio
    async def test_get_changed_files_removes_duplicates(self, application: Application):
        """Test that get_changed_files removes duplicate entries."""
        from byte.git import GitService

        # Create a file that's both modified and staged
        test_file = await self.create_test_file(application, "duplicate_test.txt", "original")

        repo = await application.make(GitService).get_repo()
        repo.index.add([str(test_file.relative_to(application.root_path()))])
        repo.index.commit("Add file")

        # Modify and stage
        test_file.write_text("modified")
        repo.index.add([str(test_file.relative_to(application.root_path()))])

        # Modify again (now it's both staged and modified)
        test_file.write_text("modified again")

        service = application.make(GitService)
        changed_files = await service.get_changed_files()

        # Count occurrences of the file
        count = sum(1 for f in changed_files if f.name == "duplicate_test.txt")
        assert count == 1

    @pytest.mark.asyncio
    async def test_commit_creates_commit_with_message(self, application: Application):
        """Test that commit creates a git commit with the provided message."""
        from byte.git import GitService

        # Create and stage a file
        test_file = await self.create_test_file(application, "commit_test.txt", "test content")

        service = application.make(GitService)
        repo = await service.get_repo()
        repo.index.add([str(test_file.relative_to(application.root_path()))])

        # Create commit
        commit_message = "feat: add test file"
        await service.commit(commit_message)

        # Verify commit was created
        latest_commit = repo.head.commit
        assert latest_commit.message.strip() == commit_message

    @pytest.mark.asyncio
    async def test_stage_changes_adds_unstaged_files(self, application: Application, mocker):
        """Test that stage_changes adds unstaged files to the index."""

        from byte.git import GitService

        # Create a file and commit it
        test_file = await self.create_test_file(application, "stage_test.txt", "original")

        service = application.make(GitService)
        repo = await service.get_repo()
        repo.index.add([str(test_file.relative_to(application.root_path()))])
        repo.index.commit("Add file")

        # Modify the file (unstaged change)
        test_file.write_text("modified")

        mocker.patch.object(service, "prompt_for_confirmation", return_value=True)

        await service.stage_changes()

        # Verify file is now staged
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        assert str(test_file.relative_to(application.root_path())) in staged_files

    @pytest.mark.asyncio
    async def test_reset_unstages_specific_file(self, application: Application):
        """Test that reset unstages a specific file."""
        from byte.git import GitService

        # Create and stage a file
        test_file = await self.create_test_file(application, "reset_test.txt", "test content")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])

        # Verify it's staged
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        assert file_path in staged_files

        # Unstage it
        await service.reset(file_path)

        # Verify it's no longer staged
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        assert file_path not in staged_files

    @pytest.mark.asyncio
    async def test_reset_unstages_all_files_when_no_path(self, application: Application):
        """Test that reset without path unstages all files."""
        from byte.git import GitService

        # Create and stage multiple files
        file1 = await self.create_test_file(application, "reset_all_1.txt", "content 1")
        file2 = await self.create_test_file(application, "reset_all_2.txt", "content 2")

        service = application.make(GitService)
        repo = await service.get_repo()
        repo.index.add(
            [str(file1.relative_to(application.root_path())), str(file2.relative_to(application.root_path()))]
        )

        # Verify files are staged
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        assert len(staged_files) >= 2

        # Unstage all
        await service.reset()

        # Verify no files are staged
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        assert len(staged_files) == 0

    @pytest.mark.asyncio
    async def test_add_stages_specific_file(self, application: Application):
        """Test that add stages a specific file."""
        from byte.git import GitService

        # Create a file
        test_file = await self.create_test_file(application, "add_test.txt", "test content")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))

        # Add the file
        await service.add(file_path)

        # Verify it's staged
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        assert file_path in staged_files

    @pytest.mark.asyncio
    async def test_remove_stages_file_deletion(self, application: Application):
        """Test that remove stages a file deletion."""
        from byte.git import GitService

        # Create, commit, then delete a file
        test_file = await self.create_test_file(application, "remove_test.txt", "test content")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])
        repo.index.commit("Add file to remove")

        # Delete the file
        test_file.unlink()

        # Stage the deletion
        await service.remove(file_path)

        # Verify deletion is staged
        staged_changes = list(repo.head.commit.diff())

        assert any(item.a_path == file_path and item.change_type == "D" for item in staged_changes)

    @pytest.mark.asyncio
    async def test_get_diff_returns_staged_changes(self, application: Application):
        """Test that get_diff with 'HEAD' returns staged changes."""
        from byte.git import GitService

        # Create and stage a file
        test_file = await self.create_test_file(application, "diff_test.txt", "test content")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])

        # Get staged diff
        diff_data = await service.get_diff()

        assert len(diff_data) > 0
        assert any(item["file"] == file_path for item in diff_data)

    @pytest.mark.asyncio
    async def test_get_diff_doesnt_returns_unstaged_changes(self, application: Application):
        """Test that get_diff without argument returns unstaged changes."""
        from byte.git import GitService

        # Create, commit, then modify a file
        test_file = await self.create_test_file(application, "unstaged_diff.txt", "original")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])
        repo.index.commit("Add file")

        # Modify without staging
        test_file.write_text("modified")

        # Get unstaged diff
        diff_data = await service.get_diff()

        assert len(diff_data) == 0
        assert not any(item["file"] == file_path for item in diff_data)

    @pytest.mark.asyncio
    async def test_get_diff_includes_change_type(self, application: Application):
        """Test that get_diff includes change_type for each file."""
        from byte.git import GitService

        # Create and stage a new file
        test_file = await self.create_test_file(application, "change_type_test.txt", "new file")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])

        diff_data = await service.get_diff()

        assert len(diff_data) > 0
        file_diff = next((item for item in diff_data if item["file"] == file_path), None)
        assert file_diff is not None
        assert "change_type" in file_diff
        assert file_diff["change_type"] in ["A", "D", "M", "R"]

    @pytest.mark.asyncio
    async def test_get_diff_includes_diff_content_for_modifications(self, application: Application):
        """Test that get_diff includes diff content for modified files."""
        from byte.git import GitService

        # Create, commit, then modify a file
        test_file = await self.create_test_file(application, "diff_content_test.txt", "original content")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])
        repo.index.commit("Add file")

        # Modify and stage
        test_file.write_text("modified content")
        repo.index.add([file_path])

        diff_data = await service.get_diff()

        file_diff = next((item for item in diff_data if item["file"] == file_path), None)
        assert file_diff is not None
        assert file_diff["diff"] is not None
        assert len(file_diff["diff"]) > 0

    @pytest.mark.asyncio
    async def test_get_diff_clears_content_for_deletions(self, application: Application):
        """Test that get_diff clears diff content for deleted files."""
        from byte.git import GitService

        # Create, commit, then delete a file
        test_file = await self.create_test_file(application, "deletion_test.txt", "content to delete")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])
        repo.index.commit("Add file to delete")

        # Delete and stage
        test_file.unlink()
        repo.index.remove([file_path])

        diff_data = await service.get_diff()

        file_diff = next((item for item in diff_data if item["file"] == file_path), None)
        assert file_diff is not None
        assert file_diff["diff"] is None

    @pytest.mark.asyncio
    async def test_get_diff_includes_status_flags(self, application: Application):
        """Test that get_diff includes is_renamed, is_modified, is_new, is_deleted flags."""
        from byte.git import GitService

        # Create and stage a new file
        test_file = await self.create_test_file(application, "flags_test.txt", "new file")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])

        diff_data = await service.get_diff()

        file_diff = next((item for item in diff_data if item["file"] == file_path), None)
        assert file_diff is not None
        assert "is_renamed" in file_diff
        assert "is_modified" in file_diff
        assert "is_new" in file_diff
        assert "is_deleted" in file_diff

    @pytest.mark.asyncio
    async def test_get_diff_includes_message(self, application: Application):
        """Test that get_diff includes a descriptive message for each change."""
        from byte.git import GitService

        # Create and stage a new file
        test_file = await self.create_test_file(application, "message_test.txt", "new file")

        service = application.make(GitService)
        repo = await service.get_repo()
        file_path = str(test_file.relative_to(application.root_path()))
        repo.index.add([file_path])

        diff_data = await service.get_diff()

        file_diff = next((item for item in diff_data if item["file"] == file_path), None)
        assert file_diff is not None
        assert "msg" in file_diff
        assert len(file_diff["msg"]) > 0
