"""Test suite for ParserService."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from byte.code_operations import (
    BaseOperationBlock,
    BlockStatus,
    BlockType,
    EditBlockService,
    NoBlocksFoundError,
    RawBlockService,
)
from byte.files import FileMode, FileService
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text
from tests.utils import create_test_file

if TYPE_CHECKING:
    from byte import Application


async def parse_and_prepare_test_blocks(application: Application, content: str, apply_blocks: bool = False):
    """ """

    file_service = application.make(FileService)

    test_file = await create_test_file(
        application,
        "file1.py",
        list_to_multiline_text(
            [
                "old content",
            ]
        ),
    )
    await file_service.add_file(test_file, FileMode.EDITABLE)

    test_file = await create_test_file(
        application,
        "file2.py",
        list_to_multiline_text(
            [
                "old content",
            ]
        ),
    )
    await file_service.add_file(test_file, FileMode.EDITABLE)

    test_file = await create_test_file(
        application,
        "file3.py",
        list_to_multiline_text(
            [
                "old content",
            ]
        ),
    )
    await file_service.add_file(test_file, FileMode.EDITABLE)

    test_file = await create_test_file(
        application,
        "duplicate_content.py",
        list_to_multiline_text(
            [
                "def old_function():",
                "    pass",
                "    return None",
                "def old_function():",
                "    pass",
                "    return None",
            ]
        ),
    )

    await file_service.add_file(test_file, FileMode.EDITABLE)

    test_file = await create_test_file(
        application,
        "template.html",
        list_to_multiline_text(
            [
                "<div>",
                "    <span>old</span>",
                "</div>",
            ]
        ),
    )
    await file_service.add_file(test_file, FileMode.EDITABLE)

    test_file = await create_test_file(
        application,
        "test.py",
        list_to_multiline_text(
            [
                "def old_function():",
                "    pass",
            ]
        ),
    )
    await file_service.add_file(test_file, FileMode.EDITABLE)

    test_file = await create_test_file(
        application,
        "multi_edit.py",
        list_to_multiline_text(
            [
                "line1",
                "line2",
                "line3",
            ]
        ),
    )
    await file_service.add_file(test_file, FileMode.EDITABLE)

    test_file = await create_test_file(application, "readonly.py", "original content")
    await file_service.add_file(test_file, FileMode.READ_ONLY)

    test_file = await create_test_file(application, "protected.py", "protected content")
    test_file.chmod(0o000)
    await file_service.add_file(test_file, FileMode.EDITABLE)

    edit_block_service = application.make(EditBlockService)
    raw_block_service = application.make(RawBlockService)

    blocks = await raw_block_service.parse_content_to_raw_blocks(content)
    blocks = await edit_block_service.convert_raw_blocks_to_parsed(blocks)  # ty:ignore[invalid-argument-type]

    if apply_blocks == True:
        blocks = [c for c in blocks if isinstance(c, BaseOperationBlock)]
        blocks = await edit_block_service.apply_blocks(blocks)

    result = []
    for block in blocks:
        if isinstance(block, BaseOperationBlock):
            result.append(block.to_dict())
        else:
            result.append(block)

    return result


@pytest.fixture
def providers():
    """Provide PromptFormatProvider for parser service tests."""
    from byte.code_operations import PromptFormatProvider
    from byte.files import FileServiceProvider

    return [FileServiceProvider, PromptFormatProvider]


@pytest.mark.asyncio
async def test_parses_simple_edit_block(application: Application):
    """Test that parser can extract a simple edit block from content."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert blocks[0].get("file_path") == "file1.py"
    assert blocks[0].get("search_content") == "old content"
    assert blocks[0].get("content") == "new content"


@pytest.mark.asyncio
async def test_parses_multiple_edit_blocks(application: Application):
    """Test that parser can extract multiple edit blocks from content."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "first replace",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            "",
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file2.py", "operation": BlockType.REPLACE, "block_id": "2"}
            ),
            "new file content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 2
    assert blocks[0].get("file_path") == "file1.py"
    assert blocks[0].get("search_content") == "old content"
    assert blocks[0].get("content") == "first replace"

    assert blocks[1].get("file_path") == "file2.py"
    assert blocks[1].get("content") == "new file content"


@pytest.mark.asyncio
async def test_raises_error_when_no_blocks_found(application: Application):
    """Test that parser raises NoBlocksFoundError when content has no file blocks."""

    content = "This is just plain text with no edit blocks."

    with pytest.raises(NoBlocksFoundError):
        await parse_and_prepare_test_blocks(application, content)


@pytest.mark.asyncio
async def test_raises_error_on_unbalanced_file_tags(application: Application):
    """Test that parser raises PreFlightUnparsableError when file tags are unbalanced."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert blocks[0].get("status") == "invalid"
    assert "Unbalanced tags" in blocks[0].get("status_message")


@pytest.mark.asyncio
async def test_parses_create_operation_block(application: Application):
    """Test that parser correctly identifies create operation blocks."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "new_file.py", "operation": BlockType.CREATE, "block_id": "1"}
            ),
            "new file content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert blocks[0].get("block_type") == "CreateFileOperationBlock"


@pytest.mark.asyncio
async def test_parses_delete_operation_block(application: Application):
    """Test that parser correctly identifies delete operation blocks."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "old_file.py", "operation": BlockType.DELETE, "block_id": "1"}
            ),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert blocks[0].get("block_type") == "DeleteFileOperationBlock"


@pytest.mark.asyncio
async def test_parses_replace_operation_block(application: Application):
    """Test that parser correctly identifies replace operation blocks."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "config.py", "operation": BlockType.REPLACE, "block_id": "1"}
            ),
            "entire new content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert blocks[0].get("block_type") == "ReplaceFileOperationBlock"


@pytest.mark.asyncio
async def test_parses_block_with_empty_replace_content(application: Application):
    """Test that parser handles blocks with empty replace content (deletion operation)."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert blocks[0].get("search_content") == "old content"
    assert blocks[0].get("content") == ""


@pytest.mark.asyncio
async def test_parses_block_with_multiline_search_replace(application: Application):
    """Test that parser handles multiline search and replace content."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "duplicate_content.py", "operation": BlockType.EDIT, "block_id": "1"},
            ),
            Boundary.open(BoundaryType.SEARCH),
            "def old_function():",
            "    pass",
            "    return None",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "def new_function():",
            "    result = calculate()",
            "    return result",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert "def old_function():" in blocks[0].get("search_content")
    assert "pass" in blocks[0].get("search_content")
    assert "return None" in blocks[0].get("search_content")
    assert "def new_function():" in blocks[0].get("content")
    assert "result = calculate()" in blocks[0].get("content")


@pytest.mark.asyncio
async def test_parses_block_with_nested_xml_like_content(application: Application):
    """Test that parser handles content that looks like XML tags."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "template.html", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "<div>",
            "    <span>old</span>",
            "</div>",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "<div>",
            "    <span>new</span>",
            "</div>",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert "<div>" in blocks[0].get("search_content")
    assert "<span>old</span>" in blocks[0].get("search_content")
    assert "<span>new</span>" in blocks[0].get("content")


@pytest.mark.asyncio
async def test_mid_flight_check_validates_read_only_file(application: Application, git_repo):
    """Test that validate_semantics marks read-only files with error status."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "readonly.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "original content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert "invalid" == blocks[0].get("status")


@pytest.mark.asyncio
async def test_mid_flight_check_validates_search_content_exists(application: Application, git_repo):
    """Test that validate_semantics validates search content can be found in file."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "def goodbye():",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "def farewell():",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert "invalid" == blocks[0].get("status")
    assert "content not found in" in blocks[0].get("status_message")


@pytest.mark.asyncio
async def test_mid_flight_check_validates_file_within_project(application: Application, git_repo):
    """Test that validate_semantics rejects files outside project root."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "/tmp/outside_project.py", "operation": BlockType.EDIT, "block_id": "1"},
            ),
            Boundary.open(BoundaryType.SEARCH),
            "def goodbye():",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "def farewell():",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert BlockStatus.INVALID == blocks[0].get("status")
    assert "File is outside project root" in blocks[0].get("status_message")


@pytest.mark.asyncio
async def test_handles_nonexistent_file_for_create(application: Application, git_repo):
    """Test that validate_semantics allows creating files that don't exist within project."""

    # Use a path that doesn't exist but is within the project
    new_file = git_repo / "new_module" / "new_file.py"

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": new_file, "operation": BlockType.CREATE, "block_id": "1"},
            ),
            "# New file content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert BlockStatus.VALID == blocks[0].get("status")


@pytest.mark.asyncio
async def test_remove_blocks_from_content_single_block(application: Application):
    """Test that remove_blocks_from_content removes a single block and replaces with summary."""

    parser_service = application.make(EditBlockService)

    content = list_to_multiline_text(
        [
            "Here's the change:",
            "",
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            "",
            "That should fix it.",
        ]
    )

    cleaned = await parser_service.remove_blocks_from_content(content)

    assert Boundary.open(BoundaryType.EDIT_BLOCK) not in cleaned
    assert Boundary.open(BoundaryType.SEARCH) not in cleaned
    assert Boundary.open(BoundaryType.REPLACE) not in cleaned
    assert "old content" not in cleaned
    assert "new content" not in cleaned
    assert "Here's the change:" in cleaned
    assert "That should fix it." in cleaned
    assert "Code change removed for brevity" in cleaned


@pytest.mark.asyncio
async def test_remove_blocks_from_content_multiple_blocks(application: Application):
    """Test that remove_blocks_from_content removes multiple blocks."""

    parser_service = application.make(EditBlockService)

    content = list_to_multiline_text(
        [
            "Making two changes:",
            "",
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "first search",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "first replace",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            "",
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file2.py", "operation": BlockType.EDIT, "block_id": "2"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "second search",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "second replace",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            "",
            "Done!",
        ]
    )

    cleaned = await parser_service.remove_blocks_from_content(content)

    assert "first search" not in cleaned
    assert "second search" not in cleaned
    assert "Making two changes:" in cleaned
    assert "Done!" in cleaned
    assert cleaned.count("Code change removed for brevity") == 2


@pytest.mark.asyncio
async def test_remove_blocks_from_content_preserves_surrounding_text(application: Application):
    """Test that remove_blocks_from_content preserves text before, between, and after blocks."""

    parser_service = application.make(EditBlockService)

    content = list_to_multiline_text(
        [
            "Introduction text here.",
            "",
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            "",
            "Middle text between blocks.",
            "",
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "other.py", "operation": BlockType.EDIT, "block_id": "2"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "more",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "different",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            "",
            "Conclusion text here.",
        ]
    )

    cleaned = await parser_service.remove_blocks_from_content(content)

    assert "Introduction text here." in cleaned
    assert "Middle text between blocks." in cleaned
    assert "Conclusion text here." in cleaned
    assert "content" not in cleaned
    assert "new content" not in cleaned
    assert "more" not in cleaned
    assert "different" not in cleaned


@pytest.mark.asyncio
async def test_apply_blocks_creates_new_file(application: Application, git_repo):
    """Test that apply_blocks creates a new file with correct content."""
    from byte.code_operations import BlockType

    new_file = git_repo / "new_module.py"

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": new_file, "operation": BlockType.CREATE, "block_id": "1"},
            ),
            "# New file content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content, True)

    assert len(blocks) == 1
    assert BlockStatus.APPLIED == blocks[0].get("status")
    assert new_file.exists()


@pytest.mark.asyncio
async def test_apply_blocks_edits_existing_file(application: Application, git_repo):
    """Test that apply_blocks modifies existing file content correctly."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "def old_function():",
            "    pass",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "def new_function():",
            "    return True",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content, True)

    assert len(blocks) == 1
    assert "applied" == blocks[0].get("status")
    test_file = Path(blocks[0].get("resolved_file_path"))
    assert test_file.read_text() == "def new_function():\n    return True"


@pytest.mark.asyncio
async def test_apply_blocks_deletes_file(application: Application, git_repo, mocker):
    """Test that apply_blocks removes files with REMOVE block type."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": BlockType.DELETE, "block_id": "1"}
            ),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content, True)

    assert len(blocks) == 1
    assert "applied" == blocks[0].get("status")
    test_file = Path(blocks[0].get("resolved_file_path"))
    assert not test_file.exists()


@pytest.mark.asyncio
async def test_apply_blocks_replaces_entire_file(application: Application, git_repo, mocker):
    """Test that apply_blocks replaces entire file content with REPLACE block type."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": BlockType.REPLACE, "block_id": "1"}
            ),
            "new_config = 'new'",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content, True)

    assert len(blocks) == 1
    assert "applied" == blocks[0].get("status")
    test_file = Path(blocks[0].get("resolved_file_path"))
    assert test_file.read_text() == "new_config = 'new'"


@pytest.mark.asyncio
async def test_apply_blocks_creates_parent_directories(application: Application, git_repo, mocker):
    """Test that apply_blocks creates parent directories when creating new files."""

    new_file = git_repo / "new_dir" / "subdir" / "module.py"
    assert not new_file.parent.exists()

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": new_file, "operation": BlockType.CREATE, "block_id": "1"},
            ),
            "# New file content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content, True)

    assert len(blocks) == 1
    assert BlockStatus.APPLIED == blocks[0].get("status")
    assert new_file.exists()
    assert new_file.read_text() == "# New file content"


@pytest.mark.asyncio
async def test_handles_permission_error_gracefully(application: Application, git_repo):
    """Test that validate_semantics handles permission errors gracefully."""
    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "protected.py", "operation": BlockType.EDIT, "block_id": "1"},
            ),
            Boundary.open(BoundaryType.SEARCH),
            "protected content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "def new_function():",
            "    return True",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    try:
        blocks = await parse_and_prepare_test_blocks(application, content, True)

        assert len(blocks) == 1
        assert BlockStatus.INVALID == blocks[0].get("status")
    finally:
        # Restore permissions for cleanup
        test_file = git_repo / "protected.py"
        test_file.chmod(0o644)


@pytest.mark.asyncio
async def test_multiple_edits_to_same_file(application: Application, git_repo):
    """Test applying multiple edit blocks to the same file sequentially."""
    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "multi_edit.py", "operation": BlockType.EDIT, "block_id": "1"},
            ),
            Boundary.open(BoundaryType.SEARCH),
            "line1",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "modified_line1",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "multi_edit.py", "operation": BlockType.EDIT, "block_id": "2"},
            ),
            Boundary.open(BoundaryType.SEARCH),
            "line3",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "modified_line3",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content, True)

    assert len(blocks) == 2
    assert BlockStatus.APPLIED == blocks[0].get("status")
    test_file = Path(blocks[0].get("resolved_file_path"))
    final_content = test_file.read_text()
    assert "modified_line1" in final_content
    assert "line2" in final_content
    assert "modified_line3" in final_content


@pytest.mark.asyncio
async def test_blocks_with_mixed_operations(application: Application, git_repo, mocker):
    """Test applying blocks with different operation types in sequence."""
    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "file1.py", "operation": BlockType.EDIT, "block_id": "1"},
            ),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "edited content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "file2.py", "operation": BlockType.DELETE, "block_id": "2"},
            ),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "file3.py", "operation": BlockType.REPLACE, "block_id": "3"},
            ),
            "replace content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": "file4.py", "operation": BlockType.CREATE, "block_id": "4"},
            ),
            "new content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content, True)

    assert len(blocks) == 4

    # AI:assert that all 4 blocks are `BlockStatus.APPLIED`
    assert BlockStatus.APPLIED == blocks[0].get("status")

    edit_file = Path(blocks[0].get("resolved_file_path"))
    assert edit_file.read_text() == "edited content"

    delete_file = Path(blocks[1].get("resolved_file_path"))
    assert not delete_file.exists()

    replace_file = Path(blocks[2].get("resolved_file_path"))
    assert replace_file.read_text() == "replace content"

    replace_file = Path(blocks[3].get("resolved_file_path"))
    assert replace_file.read_text() == "new content"


@pytest.mark.asyncio
async def test_apply_blocks_with_empty_search_appends_content(application: Application, git_repo):
    """Test that apply_blocks with empty search content appends to file."""
    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    assert len(blocks) == 1
    assert BlockStatus.INVALID == blocks[0].get("status")


@pytest.mark.asyncio
async def test_search_replace_block_to_error_format(application: Application):
    """Test that SearchReplaceBlock.to_error_format generates correct error message."""

    content = list_to_multiline_text(
        [
            Boundary.open(
                BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": BlockType.EDIT, "block_id": "1"}
            ),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    blocks = await parse_and_prepare_test_blocks(application, content)

    from byte.code_operations.blocks.file.create_file_operation_block import CreateFileOperationBlock

    create_file_operation_block = CreateFileOperationBlock(application, "1", content)

    error_format_string = create_file_operation_block.to_error_format()

    assert len(blocks) == 1
    assert error_format_string == list_to_multiline_text(
        [
            '<error operation="create" block_id="1">',
            "**File:** `file1.py`",
            "**Block ID:** 1",
            "**Status:** valid",
            "**Issue:**",
            "None",
            "</error>",
        ]
    )
