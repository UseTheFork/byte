"""Test suite for GitService.get_diff() method covering various file change scenarios."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.utils import create_test_file

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide GitServiceProvider for git service tests."""
    from byte.git import GitServiceProvider

    return [GitServiceProvider]


@pytest.mark.asyncio
async def test_get_diff_new_file_added(application: Application):
    """Test get_diff detects newly added files."""
    from byte.git import GitService

    # Create and stage a new file
    test_file = await create_test_file(application, "new_file.txt", "new content")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "A"
    assert diff_data[0]["is_new"] is True
    assert diff_data[0]["is_deleted"] is False
    assert diff_data[0]["is_modified"] is False
    assert "new:" in diff_data[0]["msg"]


@pytest.mark.asyncio
async def test_get_diff_file_deleted(application: Application):
    """Test get_diff detects deleted files."""
    from byte.git import GitService

    # Create, commit, then delete a file
    test_file = await create_test_file(application, "to_delete.txt", "content to delete")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file to delete")

    # Delete and stage the deletion
    test_file.unlink()
    repo.index.remove([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "D"
    assert diff_data[0]["is_deleted"] is True
    assert diff_data[0]["is_new"] is False
    assert diff_data[0]["is_modified"] is False
    assert diff_data[0]["diff"] is None  # No diff content for deletions
    assert "deleted:" in diff_data[0]["msg"]


@pytest.mark.asyncio
async def test_get_diff_file_modified(application: Application):
    """Test get_diff detects modified files with diff content."""
    from byte.git import GitService

    # Create, commit, then modify a file
    test_file = await create_test_file(application, "to_modify.txt", "original content\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file to modify")

    # Modify and stage
    test_file.write_text("modified content\n")
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "M"
    assert diff_data[0]["is_modified"] is True
    assert diff_data[0]["is_new"] is False
    assert diff_data[0]["is_deleted"] is False
    assert diff_data[0]["diff"] is not None
    assert len(diff_data[0]["diff"]) > 0
    assert "modified:" in diff_data[0]["msg"]
    # Verify diff contains both old and new content markers
    assert "-original content" in diff_data[0]["diff"]
    assert "+modified content" in diff_data[0]["diff"]


@pytest.mark.asyncio
async def test_get_diff_file_renamed(application: Application):
    """Test get_diff detects renamed files."""
    from byte.git import GitService

    # Create and commit a file
    test_file = await create_test_file(application, "old_name.txt", "content")

    service = application.make(GitService)
    repo = await service.get_repo()
    old_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([old_path])
    repo.index.commit("Add file to rename")

    # Rename the file
    new_file = application.root_path("new_name.txt")
    test_file.rename(new_file)
    repo.index.remove([old_path])
    new_path = str(new_file.relative_to(application.root_path()))
    repo.index.add([new_path])

    diff_data = await service.get_diff()

    # Git detects this as a rename operation
    assert len(diff_data) == 1
    assert diff_data[0]["change_type"] == "R"
    assert diff_data[0]["is_renamed"] is True
    assert diff_data[0]["file"] == old_path


@pytest.mark.asyncio
async def test_get_diff_multiple_files_mixed_changes(application: Application):
    """Test get_diff handles multiple files with different change types."""
    from byte.git import GitService

    # Create initial files and commit
    file1 = await create_test_file(application, "file1.txt", "content 1\n")
    file2 = await create_test_file(application, "file2.txt", "content 2\n")
    file3 = await create_test_file(application, "file3.txt", "content 3\n")

    service = application.make(GitService)
    repo = await service.get_repo()

    repo.index.add(
        [
            str(file1.relative_to(application.root_path())),
            str(file2.relative_to(application.root_path())),
            str(file3.relative_to(application.root_path())),
        ]
    )
    repo.index.commit("Add initial files")

    # Modify file1
    file1.write_text("modified content 1\n")
    repo.index.add([str(file1.relative_to(application.root_path()))])

    # Delete file2
    file2.unlink()
    repo.index.remove([str(file2.relative_to(application.root_path()))])

    # Add new file4
    file4 = await create_test_file(application, "file4.txt", "new content 4\n")
    repo.index.add([str(file4.relative_to(application.root_path()))])

    diff_data = await service.get_diff()

    assert len(diff_data) == 3

    # Check modified file
    modified = next((d for d in diff_data if d["file"] == str(file1.relative_to(application.root_path()))), None)
    assert modified is not None
    assert modified["is_modified"] is True

    # Check deleted file
    deleted = next((d for d in diff_data if d["file"] == str(file2.relative_to(application.root_path()))), None)
    assert deleted is not None
    assert deleted["is_deleted"] is True

    # Check new file
    added = next((d for d in diff_data if d["file"] == str(file4.relative_to(application.root_path()))), None)
    assert added is not None
    assert added["is_new"] is True


@pytest.mark.asyncio
async def test_get_diff_with_previous_commits(application: Application):
    """Test get_diff only returns changes staged for next commit, not previous commits."""
    from byte.git import GitService

    # Create and commit file1
    file1 = await create_test_file(application, "committed1.txt", "committed content 1\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    repo.index.add([str(file1.relative_to(application.root_path()))])
    repo.index.commit("First commit")

    # Create and commit file2
    file2 = await create_test_file(application, "committed2.txt", "committed content 2\n")
    repo.index.add([str(file2.relative_to(application.root_path()))])
    repo.index.commit("Second commit")

    # Now stage a new file
    file3 = await create_test_file(application, "staged.txt", "staged content\n")
    repo.index.add([str(file3.relative_to(application.root_path()))])

    diff_data = await service.get_diff()

    # Should only show the newly staged file, not the previously committed files
    assert len(diff_data) == 1
    assert diff_data[0]["file"] == str(file3.relative_to(application.root_path()))
    assert diff_data[0]["change_type"] == "A"
    assert diff_data[0]["is_new"] is True


@pytest.mark.asyncio
async def test_get_diff_empty_when_nothing_staged(application: Application):
    """Test get_diff returns empty list when nothing is staged."""
    from byte.git import GitService

    # Create and commit a file
    file1 = await create_test_file(application, "committed.txt", "committed content\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    repo.index.add([str(file1.relative_to(application.root_path()))])
    repo.index.commit("Commit file")

    # Don't stage anything new
    diff_data = await service.get_diff()

    assert len(diff_data) == 0


@pytest.mark.asyncio
async def test_get_diff_unstaged_changes(application: Application):
    """Test get_diff returns empty when changes are not staged."""
    from byte.git import GitService

    # Create, commit, then modify without staging
    test_file = await create_test_file(application, "unstaged.txt", "original\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file")

    # Modify without staging
    test_file.write_text("modified\n")

    diff_data = await service.get_diff()

    # Should be empty because changes are not staged
    assert len(diff_data) == 0


@pytest.mark.asyncio
async def test_get_diff_staged_vs_unstaged(application: Application):
    """Test get_diff only returns staged changes."""
    from byte.git import GitService

    # Create and commit two files
    file1 = await create_test_file(application, "staged_change.txt", "original 1\n")
    file2 = await create_test_file(application, "unstaged_change.txt", "original 2\n")

    service = application.make(GitService)
    repo = await service.get_repo()

    repo.index.add(
        [
            str(file1.relative_to(application.root_path())),
            str(file2.relative_to(application.root_path())),
        ]
    )
    repo.index.commit("Add files")

    # Modify and stage file1
    file1.write_text("modified 1\n")
    repo.index.add([str(file1.relative_to(application.root_path()))])

    # Modify but don't stage file2
    file2.write_text("modified 2\n")

    # Get staged changes - should only show file1
    staged_diff = await service.get_diff()
    assert len(staged_diff) == 1
    assert staged_diff[0]["file"] == str(file1.relative_to(application.root_path()))
    assert staged_diff[0]["is_modified"] is True


@pytest.mark.asyncio
async def test_get_diff_binary_file(application: Application):
    """Test get_diff handles binary files without including diff content."""
    from byte.git import GitService

    # Create and commit a binary file
    binary_file = application.root_path("binary.bin")
    binary_file.write_bytes(b"\x00\x01\x02\x03\x04")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(binary_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add binary file")

    # Modify the binary file
    binary_file.write_bytes(b"\x00\x01\x02\x03\x04\x05\x06")
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "M"
    assert diff_data[0]["is_modified"] is True
    # Binary files should not include diff content
    assert diff_data[0]["diff"] is None


@pytest.mark.asyncio
async def test_get_diff_large_file_modification(application: Application):
    """Test get_diff handles large file modifications."""
    from byte.git import GitService

    # Create a large file
    large_content = "line\n" * 1000
    test_file = await create_test_file(application, "large.txt", large_content)

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add large file")

    # Modify it
    modified_content = "modified line\n" * 1000
    test_file.write_text(modified_content)
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["is_modified"] is True
    assert diff_data[0]["diff"] is not None
    assert len(diff_data[0]["diff"]) > 0


@pytest.mark.asyncio
async def test_get_diff_file_with_special_characters(application: Application):
    """Test get_diff handles filenames with special characters."""
    from byte.git import GitService

    # Create file with special characters in name
    test_file = await create_test_file(application, "file-with_special.chars.txt", "content\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["is_new"] is True


@pytest.mark.asyncio
async def test_get_diff_nested_directory_file(application: Application):
    """Test get_diff handles files in nested directories."""
    from byte.git import GitService

    # Create nested directory structure
    nested_dir = application.root_path("dir1/dir2/dir3")
    nested_dir.mkdir(parents=True, exist_ok=True)

    test_file = nested_dir / "nested.txt"
    test_file.write_text("nested content\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["is_new"] is True
    assert "dir1/dir2/dir3/nested.txt" in diff_data[0]["file"]


@pytest.mark.asyncio
async def test_get_diff_whitespace_only_changes(application: Application):
    """Test get_diff detects whitespace-only changes."""
    from byte.git import GitService

    # Create and commit file
    test_file = await create_test_file(application, "whitespace.txt", "line1\nline2\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file")

    # Add whitespace
    test_file.write_text("line1  \nline2\n")
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["is_modified"] is True
    assert diff_data[0]["diff"] is not None


@pytest.mark.asyncio
async def test_get_diff_file_mode_change(application: Application):
    """Test get_diff when only file permissions change."""
    from byte.git import GitService

    # Create and commit a file
    test_file = await create_test_file(application, "script.sh", "#!/bin/bash\necho 'hello'\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add script")

    # Change file mode to executable
    import os

    os.chmod(test_file, 0o755)
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    # Git should detect this as a modification
    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "M"
    assert diff_data[0]["is_modified"] is True


@pytest.mark.asyncio
async def test_get_diff_empty_file_added(application: Application):
    """Test get_diff when adding a completely empty file."""
    from byte.git import GitService

    # Create an empty file
    test_file = application.root_path("empty.txt")
    test_file.touch()

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "A"
    assert diff_data[0]["is_new"] is True
    # Empty file should have no diff content
    assert diff_data[0]["diff"] == "" or diff_data[0]["diff"] is None


@pytest.mark.asyncio
async def test_get_diff_file_with_unicode_content(application: Application):
    """Test get_diff with files containing unicode/emoji characters in content."""
    from byte.git import GitService

    # Create file with unicode content
    unicode_content = "Hello 世界 🌍\nEmoji test 🚀✨\n"
    test_file = await create_test_file(application, "unicode.txt", unicode_content)

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "A"
    assert diff_data[0]["is_new"] is True


@pytest.mark.asyncio
async def test_get_diff_line_ending_changes(application: Application):
    """Test get_diff when only line endings change (LF ↔ CRLF)."""
    from byte.git import GitService

    # Create and commit file with LF endings
    test_file = await create_test_file(application, "lineendings.txt", "line1\nline2\nline3\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file with LF")

    # Change to CRLF endings
    test_file.write_text("line1\r\nline2\r\nline3\r\n")
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    # Should detect as modification
    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "M"
    assert diff_data[0]["is_modified"] is True


@pytest.mark.asyncio
async def test_get_diff_file_becomes_empty(application: Application):
    """Test get_diff when a file with content becomes empty."""
    from byte.git import GitService

    # Create and commit file with content
    test_file = await create_test_file(application, "to_empty.txt", "original content\nmore content\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file with content")

    # Make file empty
    test_file.write_text("")
    repo.index.add([file_path])

    diff_data = await service.get_diff()

    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["change_type"] == "M"
    assert diff_data[0]["is_modified"] is True
    assert diff_data[0]["diff"] is not None
    # Should show removal of content
    assert "-original content" in diff_data[0]["diff"]


@pytest.mark.asyncio
async def test_get_diff_multiple_modifications_same_file(application: Application):
    """Test get_diff shows only staged changes when file has both staged and unstaged modifications."""
    from byte.git import GitService

    # Create and commit a file
    test_file = await create_test_file(application, "multi_mod.txt", "original\n")

    service = application.make(GitService)
    repo = await service.get_repo()
    file_path = str(test_file.relative_to(application.root_path()))
    repo.index.add([file_path])
    repo.index.commit("Add file")

    # Modify and stage
    test_file.write_text("staged change\n")
    repo.index.add([file_path])

    # Modify again without staging
    test_file.write_text("unstaged change\n")

    diff_data = await service.get_diff()

    # Should only show the staged change, not the unstaged one
    assert len(diff_data) == 1
    assert diff_data[0]["file"] == file_path
    assert diff_data[0]["is_modified"] is True
    assert diff_data[0]["diff"] is not None
    # Should show staged change
    assert "+staged change" in diff_data[0]["diff"]
    # Should NOT show unstaged change
    assert "unstaged change" not in diff_data[0]["diff"]
