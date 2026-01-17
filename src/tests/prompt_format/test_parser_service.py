from __future__ import annotations

import asyncio
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
        from byte.files import FileServiceProvider
        from byte.prompt_format import PromptFormatProvider

        return [FileServiceProvider, PromptFormatProvider]

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

    @pytest.mark.asyncio
    async def test_parses_block_with_empty_search_content(self, application: Application):
        """Test that parser handles blocks with empty search content (append operation)."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "appended content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].search_content == "\n"
        assert blocks[0].replace_content == "\nappended content\n"

    @pytest.mark.asyncio
    async def test_parses_block_with_empty_replace_content(self, application: Application):
        """Test that parser handles blocks with empty replace content (deletion operation)."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "content to remove",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].search_content == "\ncontent to remove\n"
        assert blocks[0].replace_content == "\n"

    @pytest.mark.asyncio
    async def test_parses_block_with_special_characters_in_path(self, application: Application):
        """Test that parser handles file paths with special characters."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(
                    BoundaryType.FILE,
                    meta={"path": "src/my-module/file_v2.0.py", "operation": "edit", "block_id": "1"},
                ),
                Boundary.open(BoundaryType.SEARCH),
                "old",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].file_path == "src/my-module/file_v2.0.py"

    @pytest.mark.asyncio
    async def test_parses_block_with_multiline_search_replace(self, application: Application):
        """Test that parser handles multiline search and replace content."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
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
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert "def old_function():" in blocks[0].search_content
        assert "pass" in blocks[0].search_content
        assert "return None" in blocks[0].search_content
        assert "def new_function():" in blocks[0].replace_content
        assert "result = calculate()" in blocks[0].replace_content

    @pytest.mark.asyncio
    async def test_parses_block_with_nested_xml_like_content(self, application: Application):
        """Test that parser handles content that looks like XML tags."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": "template.html", "operation": "edit", "block_id": "1"}),
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
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert "<div>" in blocks[0].search_content
        assert "<span>old</span>" in blocks[0].search_content
        assert "<span>new</span>" in blocks[0].replace_content

    @pytest.mark.asyncio
    async def test_mid_flight_check_validates_read_only_file(self, application: Application, git_repo):
        """Test that mid_flight_check marks read-only files with error status."""
        from byte.files import FileMode, FileService
        from byte.prompt_format import BlockStatus, BlockType, ParserService, SearchReplaceBlock

        file_service = application.make(FileService)
        parser_service = application.make(ParserService)

        # Create a test file and add it as read-only
        test_file = (git_repo / "readonly.py").resolve()
        test_file.write_text("original content")

        await asyncio.sleep(0.1)

        await file_service.add_file(test_file, FileMode.READ_ONLY)

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="original content",
                replace_content="new content",
                block_type=BlockType.EDIT,
            )
        ]

        validated_blocks = await parser_service.mid_flight_check(blocks)

        assert len(validated_blocks) == 1
        assert validated_blocks[0].block_status == BlockStatus.READ_ONLY_ERROR
        assert "read-only" in validated_blocks[0].status_message.lower()

    @pytest.mark.asyncio
    async def test_mid_flight_check_validates_search_content_exists(self, application: Application, git_repo):
        """Test that mid_flight_check validates search content can be found in file."""
        from byte.prompt_format import BlockStatus, BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Create a test file with known content
        test_file = git_repo / "test.py"
        test_file.write_text("def hello():\n    print('hello')\n")

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="def goodbye():",
                replace_content="def farewell():",
                block_type=BlockType.EDIT,
            )
        ]

        validated_blocks = await parser_service.mid_flight_check(blocks)

        assert len(validated_blocks) == 1
        assert validated_blocks[0].block_status == BlockStatus.SEARCH_NOT_FOUND_ERROR
        assert "not found" in validated_blocks[0].status_message.lower()

    @pytest.mark.asyncio
    async def test_mid_flight_check_validates_file_within_project(self, application: Application, git_repo):
        """Test that mid_flight_check rejects files outside project root."""
        from byte.prompt_format import BlockStatus, BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Use a path outside the git repo
        outside_file = "/tmp/outside_project.py"

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=outside_file,
                search_content="",
                replace_content="new file content",
                block_type=BlockType.ADD,
            )
        ]

        validated_blocks = await parser_service.mid_flight_check(blocks)

        assert len(validated_blocks) == 1
        assert validated_blocks[0].block_status == BlockStatus.FILE_OUTSIDE_PROJECT_ERROR
        assert "project root" in validated_blocks[0].status_message.lower()

    @pytest.mark.asyncio
    async def test_mid_flight_check_strips_whitespace_for_search_match(self, application: Application, git_repo):
        """Test that mid_flight_check strips whitespace to find search content match."""
        from byte.prompt_format import BlockStatus, BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Create a test file with content
        test_file = git_repo / "test.py"
        test_file.write_text("def hello():\n    print('hello')\n")

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="  def hello():\n    print('hello')  ",
                replace_content="def hello():\n    print('hi')",
                block_type=BlockType.EDIT,
            )
        ]

        validated_blocks = await parser_service.mid_flight_check(blocks)

        assert len(validated_blocks) == 1
        assert validated_blocks[0].block_status == BlockStatus.VALID
        # Verify whitespace was stripped
        assert validated_blocks[0].search_content == "def hello():\n    print('hello')"

    @pytest.mark.asyncio
    async def test_mid_flight_check_handles_nonexistent_file_for_create(self, application: Application, git_repo):
        """Test that mid_flight_check allows creating files that don't exist within project."""
        from byte.prompt_format import BlockStatus, BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Use a path that doesn't exist but is within the project
        new_file = git_repo / "new_module" / "new_file.py"

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(new_file),
                search_content="",
                replace_content="# New file content",
                block_type=BlockType.ADD,
            )
        ]

        validated_blocks = await parser_service.mid_flight_check(blocks)

        assert len(validated_blocks) == 1
        assert validated_blocks[0].block_status == BlockStatus.VALID

    @pytest.mark.asyncio
    async def test_remove_blocks_from_content_single_block(self, application: Application):
        """Test that remove_blocks_from_content removes a single block and replaces with summary."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                "Here's the change:",
                "",
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "old content",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
                "",
                "That should fix it.",
            ]
        )

        cleaned = await parser_service.remove_blocks_from_content(content)

        assert Boundary.open(BoundaryType.FILE) not in cleaned
        assert Boundary.open(BoundaryType.SEARCH) not in cleaned
        assert Boundary.open(BoundaryType.REPLACE) not in cleaned
        assert "old content" not in cleaned
        assert "new content" not in cleaned
        assert "Here's the change:" in cleaned
        assert "That should fix it." in cleaned
        assert "Code change removed for brevity" in cleaned

    @pytest.mark.asyncio
    async def test_remove_blocks_from_content_multiple_blocks(self, application: Application):
        """Test that remove_blocks_from_content removes multiple blocks."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                "Making two changes:",
                "",
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
                "second search",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "second replace",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
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
    async def test_remove_blocks_from_content_preserves_surrounding_text(self, application: Application):
        """Test that remove_blocks_from_content preserves text before, between, and after blocks."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        content = list_to_multiline_text(
            [
                "Introduction text here.",
                "",
                Boundary.open(BoundaryType.FILE, meta={"path": "test.py", "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "content",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new content",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
                "",
                "Middle text between blocks.",
                "",
                Boundary.open(BoundaryType.FILE, meta={"path": "other.py", "operation": "edit", "block_id": "2"}),
                Boundary.open(BoundaryType.SEARCH),
                "more",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "different",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
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
    async def test_apply_blocks_creates_new_file(self, application: Application, git_repo, mocker):
        """Test that apply_blocks creates a new file with correct content."""
        from byte.prompt_format import BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Mock prompt_for_confirmation to return True
        mocker.patch.object(parser_service, "prompt_for_confirmation", return_value=True)

        new_file = git_repo / "new_module.py"
        assert not new_file.exists()

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(new_file),
                search_content="",
                replace_content="def hello():\n    print('hello')\n",
                block_type=BlockType.ADD,
            )
        ]

        await parser_service.apply_blocks(blocks)

        assert new_file.exists()
        assert new_file.read_text() == "def hello():\n    print('hello')"

    @pytest.mark.asyncio
    async def test_apply_blocks_edits_existing_file(self, application: Application, git_repo):
        """Test that apply_blocks modifies existing file content correctly."""
        from byte.prompt_format import BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        test_file = git_repo / "test.py"
        test_file.write_text("def old_function():\n    pass\n")

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="def old_function():\n    pass\n",
                replace_content="def new_function():\n    return True\n",
                block_type=BlockType.EDIT,
            )
        ]

        await parser_service.apply_blocks(blocks)

        assert test_file.read_text() == "def new_function():\n    return True\n"

    @pytest.mark.asyncio
    async def test_apply_blocks_deletes_file(self, application: Application, git_repo, mocker):
        """Test that apply_blocks removes files with REMOVE block type."""
        from byte.prompt_format import BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Mock prompt_for_confirmation to return True
        mocker.patch.object(parser_service, "prompt_for_confirmation", return_value=True)

        test_file = git_repo / "to_delete.py"
        test_file.write_text("content to delete")
        assert test_file.exists()

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="",
                replace_content="",
                block_type=BlockType.REMOVE,
            )
        ]

        await parser_service.apply_blocks(blocks)

        assert not test_file.exists()

    @pytest.mark.asyncio
    async def test_apply_blocks_replaces_entire_file(self, application: Application, git_repo, mocker):
        """Test that apply_blocks replaces entire file content with REPLACE block type."""
        from byte.prompt_format import BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Mock prompt_for_confirmation to return True
        mocker.patch.object(parser_service, "prompt_for_confirmation", return_value=True)

        test_file = git_repo / "config.py"
        test_file.write_text("old_config = 'old'\nother_line = 'keep'\n")

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="",
                replace_content="new_config = 'new'\n",
                block_type=BlockType.REPLACE,
            )
        ]

        await parser_service.apply_blocks(blocks)

        assert test_file.read_text() == "new_config = 'new'\n"

    @pytest.mark.asyncio
    async def test_apply_blocks_handles_search_not_found(self, application: Application, git_repo):
        """Test that apply_blocks handles case where search content doesn't exist."""
        from byte.prompt_format import BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        test_file = git_repo / "test.py"
        original_content = "def hello():\n    pass\n"
        test_file.write_text(original_content)

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="def goodbye():\n    pass\n",
                replace_content="def farewell():\n    pass\n",
                block_type=BlockType.EDIT,
            )
        ]

        await parser_service.apply_blocks(blocks)

        # File should remain unchanged when search content not found
        assert test_file.read_text() == original_content

    @pytest.mark.asyncio
    async def test_apply_blocks_creates_parent_directories(self, application: Application, git_repo, mocker):
        """Test that apply_blocks creates parent directories when creating new files."""
        from byte.prompt_format import BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Mock prompt_for_confirmation to return True
        mocker.patch.object(parser_service, "prompt_for_confirmation", return_value=True)

        new_file = git_repo / "new_dir" / "subdir" / "module.py"
        assert not new_file.parent.exists()

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(new_file),
                search_content="",
                replace_content="# New module\n",
                block_type=BlockType.ADD,
            )
        ]

        await parser_service.apply_blocks(blocks)

        assert new_file.exists()
        assert new_file.parent.exists()
        assert new_file.read_text() == "# New module"

    @pytest.mark.asyncio
    async def test_handles_unicode_decode_error_gracefully(self, application: Application, git_repo):
        """Test that mid_flight_check handles files with invalid UTF-8 encoding gracefully."""
        from byte.prompt_format import BlockStatus, BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Create a file with invalid UTF-8 bytes
        test_file = git_repo / "binary.dat"
        test_file.write_bytes(b"\x80\x81\x82\x83")

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="some content",
                replace_content="new content",
                block_type=BlockType.EDIT,
            )
        ]

        validated_blocks = await parser_service.mid_flight_check(blocks)

        assert len(validated_blocks) == 1
        assert validated_blocks[0].block_status == BlockStatus.SEARCH_NOT_FOUND_ERROR
        assert "cannot read" in validated_blocks[0].status_message.lower()

    @pytest.mark.asyncio
    async def test_handles_permission_error_gracefully(self, application: Application, git_repo):
        """Test that mid_flight_check handles permission errors gracefully."""
        from byte.prompt_format import BlockStatus, BlockType, ParserService, SearchReplaceBlock

        parser_service = application.make(ParserService)

        # Create a file and make it unreadable
        test_file = git_repo / "protected.py"
        test_file.write_text("protected content")
        test_file.chmod(0o000)

        blocks = [
            SearchReplaceBlock(
                block_id="1",
                file_path=str(test_file),
                search_content="protected content",
                replace_content="new content",
                block_type=BlockType.EDIT,
            )
        ]

        try:
            validated_blocks = await parser_service.mid_flight_check(blocks)

            assert len(validated_blocks) == 1
            assert validated_blocks[0].block_status == BlockStatus.SEARCH_NOT_FOUND_ERROR
            assert "cannot read" in validated_blocks[0].status_message.lower()
        finally:
            # Restore permissions for cleanup
            test_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_full_workflow_parse_validate_apply(self, application: Application, git_repo):
        """Test complete workflow from parsing through validation to application."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        # Create initial file
        test_file = git_repo / "workflow_test.py"
        test_file.write_text("def old_function():\n    pass\n")

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": str(test_file), "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "def old_function():\n    pass\n",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "def new_function():\n    return True\n",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        # Parse
        blocks = await parser_service.parse_content_to_blocks(content)
        assert len(blocks) == 1

        # Validate
        validated_blocks = await parser_service.mid_flight_check(blocks)
        assert validated_blocks[0].block_status.value == "valid"

        # Apply
        await parser_service.apply_blocks(validated_blocks)
        assert test_file.read_text() == "def new_function():\n    return True\n"

    @pytest.mark.asyncio
    async def test_multiple_edits_to_same_file(self, application: Application, git_repo):
        """Test applying multiple edit blocks to the same file sequentially."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        test_file = git_repo / "multi_edit.py"
        test_file.write_text("line1\nline2\nline3\n")

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": str(test_file), "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "line1\n",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "modified_line1\n",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
                "",
                Boundary.open(BoundaryType.FILE, meta={"path": str(test_file), "operation": "edit", "block_id": "2"}),
                Boundary.open(BoundaryType.SEARCH),
                "line3\n",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "modified_line3\n",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)
        assert len(blocks) == 2

        validated_blocks = await parser_service.mid_flight_check(blocks)
        await parser_service.apply_blocks(validated_blocks)

        final_content = test_file.read_text()
        assert "modified_line1" in final_content
        assert "line2" in final_content
        assert "modified_line3" in final_content

    @pytest.mark.asyncio
    async def test_blocks_with_mixed_operations(self, application: Application, git_repo, mocker):
        """Test applying blocks with different operation types in sequence."""
        from byte.prompt_format import ParserService

        parser_service = application.make(ParserService)

        # Mock prompt_for_confirmation to return True
        mocker.patch.object(parser_service, "prompt_for_confirmation", return_value=True)

        # Create initial files
        edit_file = git_repo / "to_edit.py"
        edit_file.write_text("original content\n")

        delete_file = git_repo / "to_delete.py"
        delete_file.write_text("delete me\n")

        create_file = git_repo / "to_create.py"

        content = list_to_multiline_text(
            [
                Boundary.open(BoundaryType.FILE, meta={"path": str(edit_file), "operation": "edit", "block_id": "1"}),
                Boundary.open(BoundaryType.SEARCH),
                "original content\n",
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "edited content\n",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
                "",
                Boundary.open(
                    BoundaryType.FILE, meta={"path": str(delete_file), "operation": "delete", "block_id": "2"}
                ),
                Boundary.open(BoundaryType.SEARCH),
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
                "",
                Boundary.open(
                    BoundaryType.FILE, meta={"path": str(create_file), "operation": "create", "block_id": "3"}
                ),
                Boundary.open(BoundaryType.SEARCH),
                Boundary.close(BoundaryType.SEARCH),
                Boundary.open(BoundaryType.REPLACE),
                "new file content\n",
                Boundary.close(BoundaryType.REPLACE),
                Boundary.close(BoundaryType.FILE),
            ]
        )

        blocks = await parser_service.parse_content_to_blocks(content)
        assert len(blocks) == 3

        validated_blocks = await parser_service.mid_flight_check(blocks)
        await parser_service.apply_blocks(validated_blocks)

        assert edit_file.read_text() == "edited content\n"
        assert not delete_file.exists()
        assert create_file.exists()
        assert create_file.read_text() == "new file content"
