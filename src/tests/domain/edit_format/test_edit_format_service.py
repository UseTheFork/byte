"""Comprehensive test suite for EditFormatService.

Tests the complete lifecycle of edit format operations including parsing,
validation, and application of search/replace blocks.
"""

from pathlib import Path
from textwrap import dedent

import pytest

from byte.domain.edit_format.exceptions import PreFlightCheckError
from byte.domain.edit_format.service.edit_format_service import (
    BlockStatus,
    BlockType,
    EditFormatService,
    SearchReplaceBlock,
)
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.file_service import FileService


class TestEditFormatServiceParsing:
    """Test suite for parsing SEARCH/REPLACE blocks from content."""

    @pytest.mark.asyncio
    async def test_parse_single_edit_block(
        self, edit_format_service: EditFormatService
    ):
        """Test parsing a single edit block with proper formatting."""
        content = dedent("""
        I'll modify the file to add an import.

        ```python
        +++++++ src/main.py
        <<<<<<< SEARCH
        from flask import Flask
        =======
        import math
        from flask import Flask
        >>>>>>> REPLACE
        ```
        """)

        blocks = edit_format_service.parse_content_to_blocks(content)

        print(blocks)

        assert len(blocks) == 1
        assert blocks[0].operation == "+++++++"
        assert blocks[0].file_path == "src/main.py"
        assert blocks[0].search_content == "from flask import Flask"
        assert blocks[0].replace_content == "import math\nfrom flask import Flask"

    @pytest.mark.asyncio
    async def test_parse_multiple_edit_blocks(
        self, edit_format_service: EditFormatService
    ):
        """Test parsing multiple SEARCH/REPLACE blocks in sequence."""
        content = dedent("""
        I'll make two changes to the file.

        ```python
        +++++++ src/main.py
        <<<<<<< SEARCH
        from flask import Flask
        =======
        import math
        from flask import Flask
        >>>>>>> REPLACE
        ```

        ```python
        +++++++ src/main.py
        <<<<<<< SEARCH
        def calculate():
            pass
        =======
        def calculate():
            return 42
        >>>>>>> REPLACE
        ```
        """)

        blocks = edit_format_service.parse_content_to_blocks(content)

        assert len(blocks) == 2
        assert blocks[0].file_path == "src/main.py"
        assert blocks[1].file_path == "src/main.py"
        assert "import math" in blocks[0].replace_content
        assert "return 42" in blocks[1].replace_content

    @pytest.mark.asyncio
    async def test_parse_new_file_creation(
        self, edit_format_service: EditFormatService
    ):
        """Test parsing a block for creating a new file (empty SEARCH section)."""
        content = dedent("""
        I'll create a new file.

        ```python
        +++++++ src/new_file.py
        <<<<<<< SEARCH
        =======
        def hello():
            print("Hello, World!")
        >>>>>>> REPLACE
        ```
        """)

        blocks = edit_format_service.parse_content_to_blocks(content)

        print(blocks)

        assert len(blocks) == 1
        assert blocks[0].operation == "+++++++"
        assert blocks[0].file_path == "src/new_file.py"
        assert blocks[0].search_content == ""
        assert "def hello():" in blocks[0].replace_content

    @pytest.mark.asyncio
    async def test_parse_file_removal(self, edit_format_service: EditFormatService):
        """Test parsing a block for removing a file."""
        content = dedent("""
        I'll remove the old file.
        ```python
        ------- src/old_file.py
        <<<<<<< SEARCH
        =======
        >>>>>>> REPLACE
        ```
        """)

        blocks = edit_format_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].operation == "-------"
        assert blocks[0].file_path == "src/old_file.py"
        assert blocks[0].search_content == ""
        assert blocks[0].replace_content == ""

    @pytest.mark.asyncio
    async def test_parse_replace_entire_file(
        self, edit_format_service: EditFormatService
    ):
        """Test parsing a block for replacing entire file contents."""
        content = dedent("""
        I'll replace all the file contents.

        ```python
        ------- src/config.py
        <<<<<<< SEARCH
        =======
        NEW_CONFIG = {"key": "value"}
        >>>>>>> REPLACE
        ```
        """)

        blocks = edit_format_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].operation == "-------"
        assert blocks[0].search_content == ""
        assert "NEW_CONFIG" in blocks[0].replace_content

    @pytest.mark.asyncio
    async def test_parse_no_blocks(self, edit_format_service: EditFormatService):
        """Test parsing content with no SEARCH/REPLACE blocks."""
        content = "This is just some text without any blocks."

        blocks = edit_format_service.parse_content_to_blocks(content)

        assert len(blocks) == 0


class TestEditFormatServiceValidation:
    """Test suite for validation of edit blocks."""

    @pytest.mark.asyncio
    async def test_preflight_check_balanced_markers(
        self, edit_format_service: EditFormatService
    ):
        """Test pre-flight check passes with balanced markers."""
        content = dedent("""
        ```python
        +++++++ file.py
        <<<<<<< SEARCH
        old
        =======
        new
        >>>>>>> REPLACE
        ```
        """)

        # Should not raise an exception
        edit_format_service.pre_flight_check(content)

    @pytest.mark.asyncio
    async def test_preflight_check_unbalanced_markers(
        self, edit_format_service: EditFormatService
    ):
        """Test pre-flight check fails with unbalanced markers."""
        content = dedent("""
        ```python
        +++++++ file.py
        <<<<<<< SEARCH
        old
        =======
        new
        ```
        """)

        with pytest.raises(
            PreFlightCheckError, match="Malformed SEARCH/REPLACE blocks"
        ):
            edit_format_service.pre_flight_check(content)

    @pytest.mark.asyncio
    async def test_midflight_check_existing_file_valid_search(
        self,
        edit_format_service: EditFormatService,
        create_test_file,
        sample_file_content: str,
    ):
        """Test mid-flight validation passes for existing file with valid search content."""
        # Create a test file
        test_file = create_test_file("src/utils.py", sample_file_content)

        # Create a block that searches for content that exists
        blocks = [
            SearchReplaceBlock(
                operation="+++++++",
                file_path=str(test_file),
                search_content="from rich.pretty import pprint",
                replace_content="import rich\nfrom rich.pretty import pprint",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert validated_blocks[0].block_status == BlockStatus.VALID
        assert validated_blocks[0].block_type == BlockType.EDIT

    @pytest.mark.asyncio
    async def test_midflight_check_search_not_found(
        self,
        edit_format_service: EditFormatService,
        create_test_file,
        sample_file_content: str,
    ):
        """Test mid-flight validation fails when search content not found."""
        # Create a test file
        test_file = create_test_file("src/utils.py", sample_file_content)

        # Create a block that searches for content that doesn't exist
        blocks = [
            SearchReplaceBlock(
                operation="+++++++",
                file_path=str(test_file),
                search_content="THIS CONTENT DOES NOT EXIST",
                replace_content="new content",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert validated_blocks[0].block_status == BlockStatus.SEARCH_NOT_FOUND_ERROR
        assert "not found" in validated_blocks[0].status_message.lower()

    @pytest.mark.asyncio
    async def test_midflight_check_new_file_within_project(
        self,
        edit_format_service: EditFormatService,
        tmp_project_root: Path,
    ):
        """Test mid-flight validation passes for new file within project."""
        # Create a block for a new file within the project
        new_file_path = tmp_project_root / "src" / "new_file.py"
        blocks = [
            SearchReplaceBlock(
                operation="+++++++",
                file_path=str(new_file_path),
                search_content="",
                replace_content="def hello(): pass",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert validated_blocks[0].block_status == BlockStatus.VALID
        assert validated_blocks[0].block_type == BlockType.ADD

    @pytest.mark.asyncio
    async def test_midflight_check_new_file_outside_project(
        self,
        edit_format_service: EditFormatService,
        tmp_path: Path,
    ):
        """Test mid-flight validation fails for new file outside project."""

        # Create a block for a new file outside the project
        # Make sure the outside directory is definitely outside tmp_project_root
        outside_dir = tmp_path.parent / "definitely_outside"
        outside_dir.mkdir(exist_ok=True)
        outside_file = outside_dir / "file.py"

        blocks = [
            SearchReplaceBlock(
                operation="+++++++",
                file_path=str(outside_file),
                search_content="",
                replace_content="def hello(): pass",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert (
            validated_blocks[0].block_status == BlockStatus.FILE_OUTSIDE_PROJECT_ERROR
        )
        assert "project root" in validated_blocks[0].status_message.lower()

    @pytest.mark.asyncio
    async def test_midflight_check_readonly_file(
        self,
        edit_format_service: EditFormatService,
        file_service: FileService,
        create_test_file,
        sample_file_content: str,
    ):
        """Test mid-flight validation fails for read-only files."""
        # Create a test file and add it as read-only
        test_file = create_test_file("src/readonly.py", sample_file_content)
        await file_service.add_file(test_file, FileMode.READ_ONLY)

        blocks = [
            SearchReplaceBlock(
                operation="+++++++",
                file_path=str(test_file),
                search_content="import sys",
                replace_content="import os\nimport sys",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert validated_blocks[0].block_status == BlockStatus.READ_ONLY_ERROR
        assert "read-only" in validated_blocks[0].status_message.lower()


class TestEditFormatServiceBlockTypes:
    """Test suite for determining block types correctly."""

    @pytest.mark.asyncio
    async def test_block_type_add_for_new_file_with_plus_operation(
        self,
        edit_format_service: EditFormatService,
        tmp_project_root: Path,
    ):
        """Test that +++++++ operation with non-existent file sets BlockType.ADD."""
        new_file = tmp_project_root / "new_file.py"
        blocks = [
            SearchReplaceBlock(
                operation="+++++++",
                file_path=str(new_file),
                search_content="",
                replace_content="content",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert validated_blocks[0].block_type == BlockType.ADD

    @pytest.mark.asyncio
    async def test_block_type_edit_for_existing_file_with_plus_operation(
        self,
        edit_format_service: EditFormatService,
        create_test_file,
    ):
        """Test that +++++++ operation with existing file sets BlockType.EDIT."""
        existing_file = create_test_file("existing.py", "old content")
        blocks = [
            SearchReplaceBlock(
                operation="+++++++",
                file_path=str(existing_file),
                search_content="old",
                replace_content="new",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert validated_blocks[0].block_type == BlockType.EDIT

    @pytest.mark.asyncio
    async def test_block_type_remove_for_minus_operation_empty_content(
        self,
        edit_format_service: EditFormatService,
        create_test_file,
    ):
        """Test that ------- operation with empty search/replace sets BlockType.REMOVE."""
        existing_file = create_test_file("to_remove.py", "content")
        blocks = [
            SearchReplaceBlock(
                operation="-------",
                file_path=str(existing_file),
                search_content="",
                replace_content="",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert validated_blocks[0].block_type == BlockType.REMOVE

    @pytest.mark.asyncio
    async def test_block_type_edit_for_minus_operation_with_content(
        self,
        edit_format_service: EditFormatService,
        create_test_file,
    ):
        """Test that ------- operation with replace content sets BlockType.EDIT (full replacement)."""
        existing_file = create_test_file("to_replace.py", "old content")
        blocks = [
            SearchReplaceBlock(
                operation="-------",
                file_path=str(existing_file),
                search_content="",
                replace_content="new content",
            )
        ]

        validated_blocks = await edit_format_service.mid_flight_check(blocks)

        assert validated_blocks[0].block_type == BlockType.EDIT


class TestEditFormatServiceUtilities:
    """Test suite for utility methods."""

    @pytest.mark.asyncio
    async def test_remove_blocks_from_content(
        self, edit_format_service: EditFormatService
    ):
        """Test that SEARCH/REPLACE blocks are removed and replaced with summary."""
        content = dedent("""
        I'll make this change:

        ```python
        +++++++ file.py
        <<<<<<< SEARCH
        old
        =======
        new
        >>>>>>> REPLACE
        ```

        That should do it!
        """)

        cleaned = edit_format_service.remove_blocks_from_content(content)

        assert "<<<<<<< SEARCH" not in cleaned
        assert ">>>>>>> REPLACE" not in cleaned
        assert "Changes applied to `file.py`" in cleaned
        assert "That should do it!" in cleaned

    @pytest.mark.asyncio
    async def test_to_search_replace_format(self):
        """Test converting SearchReplaceBlock back to formatted string."""
        block = SearchReplaceBlock(
            operation="+++++++",
            file_path="test.py",
            search_content="old",
            replace_content="new",
        )

        formatted = block.to_search_replace_format()

        assert "+++++++ test.py" in formatted
        assert "<<<<<<< SEARCH" in formatted
        assert "=======" in formatted
        assert ">>>>>>> REPLACE" in formatted
        assert "old" in formatted
        assert "new" in formatted


class TestEditFormatServiceIntegration:
    """Integration tests for the complete edit format workflow."""

    @pytest.mark.asyncio
    async def test_handle_complete_workflow_new_file(
        self,
        edit_format_service: EditFormatService,
        tmp_project_root: Path,
        monkeypatch,
    ):
        """Test complete workflow: parse, validate, and apply for new file creation.

        This is the regression test for the reported issue where replace content
        was being taken from the wrong block.
        """

        # Mock user confirmation to always return True
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            edit_format_service, "prompt_for_confirmation", mock_confirm
        )

        content = dedent("""
        I'll create a new file:

        ```python
        +++++++ src/new_module.py
        <<<<<<< SEARCH
        =======
        def hello():
            print("Hello, World!")
        >>>>>>> REPLACE
        ```
        """)

        blocks = await edit_format_service.handle(content)

        assert len(blocks) == 1
        assert blocks[0].block_status == BlockStatus.VALID
        assert blocks[0].block_type == BlockType.ADD

        # Verify the file was created with correct content
        new_file = tmp_project_root / "src" / "new_module.py"
        assert new_file.exists()
        content = new_file.read_text()
        assert "def hello():" in content
        assert "Hello, World!" in content

    @pytest.mark.asyncio
    async def test_handle_multiple_blocks_same_file(
        self,
        edit_format_service: EditFormatService,
        create_test_file,
        monkeypatch,
    ):
        """Test handling multiple edit blocks for the same file."""

        # Mock user confirmation to always return True
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            edit_format_service, "prompt_for_confirmation", mock_confirm
        )

        # Create initial file
        initial_content = "line1\nline2\nline3\n"
        test_file = create_test_file("test.py", initial_content)

        content = dedent(f"""
        I'll make two changes:

        ```python
        +++++++ {test_file}
        <<<<<<< SEARCH
        line1
        =======
        new_line1
        >>>>>>> REPLACE
        ```

        ```python
        +++++++ {test_file}
        <<<<<<< SEARCH
        line3
        =======
        new_line3
        >>>>>>> REPLACE
        ```
        """)

        blocks = await edit_format_service.handle(content)

        assert len(blocks) == 2
        assert all(b.block_status == BlockStatus.VALID for b in blocks)

        # Verify changes were applied
        final_content = test_file.read_text()
        assert "new_line1" in final_content
        assert "line2" in final_content
        assert "new_line3" in final_content
