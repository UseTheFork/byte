from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from byte.prompt_format import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestParserService(BaseTest):
    """Test suite for ParserService."""

    @pytest.fixture
    def providers(self):
        """Provide PromptFormatProvider for parser service tests."""
        from byte.prompt_format import PromptFormatProvider

        return [PromptFormatProvider]

    @pytest.mark.asyncio
    async def test_parser_service_boots_successfully(self, application: Application):
        """Test that parser service initializes without errors."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        # Service should be booted and have required attributes
        assert parser_service is not None
        assert hasattr(parser_service, "prompts")
        assert hasattr(parser_service, "edit_blocks")

    @pytest.mark.asyncio
    async def test_parses_simple_edit_block(self, application: Application):
        """Test that parser can extract a simple edit block from content."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "old content ",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].file_path == "test.py"
        assert blocks[0].search_content == "\nold content\n"
        assert blocks[0].replace_content == "\nnew content\n"

    @pytest.mark.asyncio
    async def test_parses_multiple_edit_blocks(self, application: Application):
        """Test that parser can extract multiple edit blocks from content."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "file1.py", "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "first search",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "first replace",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
                "",
                Boundary.open(BoundaryType.FILE, meta={"path": "file2.py", "operation": "edit", "block_id": "2"}),
                Boundary.open(BoundaryType.SEARCH),
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new file content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 2
        assert blocks[0].file_path == "file1.py"
        assert blocks[0].search_content == "\nfirst search\n"
        assert blocks[0].replace_content == "\nfirst replace\n"
        assert blocks[1].file_path == "file2.py"
        assert blocks[1].search_content == "\n"
        assert blocks[1].replace_content == "\nnew file content\n"

    @pytest.mark.asyncio
    async def test_raises_error_when_no_blocks_found(self, application: Application):
        """Test that parser raises NoBlocksFoundError when content has no file blocks."""
        from byte.prompt_format import NoBlocksFoundError, ParserService

        parser_service = application.make(ParserService)

        content = "This is just plain text with no edit blocks."

        with pytest.raises(NoBlocksFoundError):
            await parser_service.check_blocks_exist(content)

    @pytest.mark.asyncio
    async def test_raises_error_on_unbalanced_file_tags(self, application: Application):
        """Test that parser raises PreFlightUnparsableError when file tags are unbalanced."""
        from byte.prompt_format import ParserService, PreFlightUnparsableError

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "content",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new content",
                Boundary.close(BoundaryType.REPLACE),
            ]
        )

        with pytest.raises(
            PreFlightUnparsableError,
            match=f"{Boundary.open(BoundaryType.FILE)} tags=1, {Boundary.close(BoundaryType.FILE)} tags=0",
        ):
            await parser_service.check_file_tags_balanced(content)

    @pytest.mark.asyncio
    async def test_raises_error_on_missing_block_ids(self, application: Application):
        """Test that parser raises PreFlightUnparsableError when file blocks lack block_id."""
        from byte.prompt_format import ParserService, PreFlightUnparsableError

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "edit"}),
                Boundary.open(BoundaryType.SEARCH),
                "content",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        with pytest.raises(PreFlightUnparsableError, match="missing block_id attribute"):
            await parser_service.check_block_ids(content)

    @pytest.mark.asyncio
    async def test_parses_create_operation_block(self, application: Application):
        """Test that parser correctly identifies create operation blocks."""
        from byte.prompt_format import BlockType, ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "new_file.py", "operation": "create", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new file content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].block_type == BlockType.ADD

    @pytest.mark.asyncio
    async def test_parses_delete_operation_block(self, application: Application):
        """Test that parser correctly identifies delete operation blocks."""
        from byte.prompt_format import BlockType, ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "old_file.py", "operation": "delete", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].block_type == BlockType.REMOVE

    @pytest.mark.asyncio
    async def test_parses_replace_operation_block(self, application: Application):
        """Test that parser correctly identifies replace operation blocks."""
        from byte.prompt_format import BlockType, ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "config.py", "operation": "replace", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "entire new content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].block_type == BlockType.REPLACE

    @pytest.mark.asyncio
    async def test_defaults_to_edit_for_unknown_operation(self, application: Application):
        """Test that parser defaults to EDIT block type for unknown operations."""
        from byte.prompt_format import BlockType, ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "unknown", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "old content",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].block_type == BlockType.EDIT
