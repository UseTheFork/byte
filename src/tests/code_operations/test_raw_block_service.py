"""Test suite for RawBlockService."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from byte.code_operations import PreFlightUnparsableError, RawBlockService
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide PromptFormatProvider for raw block service tests."""
    from byte.code_operations import PromptFormatProvider
    from byte.files import FileServiceProvider

    return [FileServiceProvider, PromptFormatProvider]


@pytest.mark.asyncio
async def test_parses_simple_raw_block(application: Application):
    """Test that RawBlockService can extract a simple raw block from content."""

    raw_block_service = application.make(RawBlockService)

    content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    raw_blocks = await raw_block_service.parse_content_to_raw_blocks(content)

    assert len(raw_blocks) == 1
    assert raw_blocks[0].block_id == "1"
    assert "test.py" in raw_blocks[0].raw_content
    assert "old content" in raw_blocks[0].raw_content
    assert "new content" in raw_blocks[0].raw_content


@pytest.mark.asyncio
async def test_parses_multiple_raw_blocks(application: Application):
    """Test that RawBlockService can extract multiple raw blocks from content."""

    raw_block_service = application.make(RawBlockService)

    content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": "edit", "block_id": "1"}),
            Boundary.open(BoundaryType.SEARCH),
            "first search",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "first replace",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            "",
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "file2.py", "operation": "edit", "block_id": "2"}),
            Boundary.open(BoundaryType.SEARCH),
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new file content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    raw_blocks = await raw_block_service.parse_content_to_raw_blocks(content)

    assert len(raw_blocks) == 2
    assert raw_blocks[0].block_id == "1"
    assert "file1.py" in raw_blocks[0].raw_content
    assert "first search" in raw_blocks[0].raw_content
    assert "first replace" in raw_blocks[0].raw_content
    assert raw_blocks[1].block_id == "2"
    assert "file2.py" in raw_blocks[1].raw_content
    assert "new file content" in raw_blocks[1].raw_content


@pytest.mark.asyncio
async def test_parses_invalid_raw_block(application: Application):
    """Test that RawBlockService detects and marks blocks with unbalanced tags."""

    raw_block_service = application.make(RawBlockService)

    content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            # Missing closing edit_block tag
        ]
    )

    with pytest.raises(PreFlightUnparsableError) as exc_info:
        await raw_block_service.parse_content_to_raw_blocks(content)

    assert "Unbalanced tags" in str(exc_info.value) or "<edit_block>" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_block_id_not_number(application: Application):
    """Test that RawBlockService raises error when block_id is not a number."""

    raw_block_service = application.make(RawBlockService)

    content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": "edit", "block_id": "abc"}),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    with pytest.raises(PreFlightUnparsableError) as exc_info:
        await raw_block_service.parse_content_to_raw_blocks(content)

    assert "block_id must be a number" in str(exc_info.value)


@pytest.mark.asyncio
async def test_missing_block_id(application: Application):
    """Test that RawBlockService raises error when block_id is missing."""

    raw_block_service = application.make(RawBlockService)

    content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": "edit"}),
            Boundary.open(BoundaryType.SEARCH),
            "old content",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new content",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    with pytest.raises(PreFlightUnparsableError) as exc_info:
        await raw_block_service.parse_content_to_raw_blocks(content)

    assert "missing block_id" in str(exc_info.value)


@pytest.mark.asyncio
async def test_merge_iterations_replaces_blocks_by_id(application: Application):
    """Test that merge_iterations replaces blocks with matching block_id."""
    from langchain_core.messages import AIMessage

    raw_block_service = application.make(RawBlockService)

    # First message with block_id="1"
    first_content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
            Boundary.open(BoundaryType.SEARCH),
            "old search",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "old replace",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    # Second message with updated block_id="1"
    second_content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
            Boundary.open(BoundaryType.SEARCH),
            "new search",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "new replace",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    messages = [AIMessage(content=first_content), AIMessage(content=second_content)]

    final_components = await raw_block_service.merge_iterations(messages)

    # Should have only one block (replaced)
    from byte.code_operations import RawSearchReplaceBlock

    blocks = [c for c in final_components if isinstance(c, RawSearchReplaceBlock)]
    assert len(blocks) == 1
    assert "new search" in blocks[0].raw_content
    assert "new replace" in blocks[0].raw_content
    assert "old search" not in blocks[0].raw_content


@pytest.mark.asyncio
async def test_merge_iterations_preserves_text_between_blocks(application: Application):
    """Test that merge_iterations preserves text content between blocks."""
    from langchain_core.messages import AIMessage

    raw_block_service = application.make(RawBlockService)

    first_content = list_to_multiline_text(
        [
            "Here's my first change:",
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
            Boundary.open(BoundaryType.SEARCH),
            "search",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "replace",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
            "That should work.",
        ]
    )

    messages = [AIMessage(content=first_content)]

    final_components = await raw_block_service.merge_iterations(messages)

    # Should have text before, block, and text after
    assert len(final_components) == 3
    assert isinstance(final_components[0], str)
    assert "Here's my first change:" in final_components[0]
    from byte.code_operations import RawSearchReplaceBlock

    assert isinstance(final_components[1], RawSearchReplaceBlock)
    assert isinstance(final_components[2], str)
    assert "That should work." in final_components[2]


@pytest.mark.asyncio
async def test_merge_iterations_adds_new_blocks(application: Application):
    """Test that merge_iterations adds new blocks that weren't in previous iterations."""
    from langchain_core.messages import AIMessage

    raw_block_service = application.make(RawBlockService)

    first_content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "file1.py", "operation": "edit", "block_id": "1"}),
            Boundary.open(BoundaryType.SEARCH),
            "search1",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "replace1",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    second_content = list_to_multiline_text(
        [
            Boundary.open(BoundaryType.EDIT_BLOCK, meta={"path": "file2.py", "operation": "edit", "block_id": "2"}),
            Boundary.open(BoundaryType.SEARCH),
            "search2",
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            "replace2",
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]
    )

    messages = [AIMessage(content=first_content), AIMessage(content=second_content)]

    final_components = await raw_block_service.merge_iterations(messages)

    from byte.code_operations import RawSearchReplaceBlock

    blocks = [c for c in final_components if isinstance(c, RawSearchReplaceBlock)]
    assert len(blocks) == 2
    assert blocks[0].block_id == "1"
    assert blocks[1].block_id == "2"
