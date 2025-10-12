"""Comprehensive test suite for EditBlockService.

Tests the complete lifecycle of edit format operations including parsing,
validation, and application of search/replace blocks.
"""

from pathlib import Path
from textwrap import dedent

import pytest

from byte.domain.edit_format.exceptions import PreFlightCheckError
from byte.domain.edit_format.models import BlockType
from byte.domain.edit_format.service.edit_block_service import EditBlockService
from byte.domain.edit_format.service.edit_format_service import (
	BlockStatus,
	SearchReplaceBlock,
)
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.file_service import FileService


class TestEditBlockServiceParsing:
	"""Test suite for parsing SEARCH/REPLACE blocks from content."""

	@pytest.mark.asyncio
	async def test_parse_single_edit_block(self, edit_format_service: EditBlockService):
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

		assert len(blocks) == 1
		assert blocks[0].operation == "+++++++"
		assert blocks[0].file_path == "src/main.py"
		assert blocks[0].search_content == "from flask import Flask"
		assert blocks[0].replace_content == "import math\nfrom flask import Flask"

	@pytest.mark.asyncio
	async def test_parse_multiple_edit_blocks(self, edit_format_service: EditBlockService):
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
	async def test_parse_new_file_creation(self, edit_format_service: EditBlockService):
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
	async def test_parse_file_removal(self, edit_format_service: EditBlockService):
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
	async def test_parse_replace_entire_file(self, edit_format_service: EditBlockService):
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
	async def test_parse_no_blocks(self, edit_format_service: EditBlockService):
		"""Test parsing content with no SEARCH/REPLACE blocks."""
		content = "This is just some text without any blocks."

		blocks = edit_format_service.parse_content_to_blocks(content)

		assert len(blocks) == 0


class TestEditBlockServiceValidation:
	"""Test suite for validation of edit blocks."""

	@pytest.mark.asyncio
	async def test_preflight_check_balanced_markers(self, edit_format_service: EditBlockService):
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
	async def test_preflight_check_unbalanced_markers(self, edit_format_service: EditBlockService):
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

		with pytest.raises(PreFlightCheckError, match="Malformed SEARCH/REPLACE blocks"):
			edit_format_service.pre_flight_check(content)

	@pytest.mark.asyncio
	async def test_midflight_check_existing_file_valid_search(
		self,
		edit_format_service: EditBlockService,
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
		edit_format_service: EditBlockService,
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
		edit_format_service: EditBlockService,
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
		edit_format_service: EditBlockService,
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

		assert validated_blocks[0].block_status == BlockStatus.FILE_OUTSIDE_PROJECT_ERROR
		assert "project root" in validated_blocks[0].status_message.lower()

	@pytest.mark.asyncio
	async def test_midflight_check_readonly_file(
		self,
		edit_format_service: EditBlockService,
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


class TestEditBlockServiceBlockTypes:
	"""Test suite for determining block types correctly."""

	@pytest.mark.asyncio
	async def test_block_type_add_for_new_file_with_plus_operation(
		self,
		edit_format_service: EditBlockService,
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
		edit_format_service: EditBlockService,
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
		edit_format_service: EditBlockService,
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
		edit_format_service: EditBlockService,
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


class TestEditBlockServiceUtilities:
	"""Test suite for utility methods."""

	@pytest.mark.asyncio
	async def test_remove_blocks_from_content(self, edit_format_service: EditBlockService):
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


class TestEditBlockServiceIntegration:
	"""Integration tests for the complete edit format workflow."""

	@pytest.mark.asyncio
	async def test_handle_complete_workflow_new_file(
		self,
		edit_format_service: EditBlockService,
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

		monkeypatch.setattr(edit_format_service, "prompt_for_confirmation", mock_confirm)

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
		edit_format_service: EditBlockService,
		create_test_file,
		monkeypatch,
	):
		"""Test handling multiple edit blocks for the same file."""

		# Mock user confirmation to always return True
		async def mock_confirm(message, default):
			return True

		monkeypatch.setattr(edit_format_service, "prompt_for_confirmation", mock_confirm)

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

	@pytest.mark.asyncio
	async def test_handle_multiple_blocks_across_multiple_files(
		self,
		edit_format_service: EditBlockService,
		create_test_file,
		tmp_project_root: Path,
		monkeypatch,
	):
		"""Test handling multiple edit blocks across different files with mixed operations.

		Tests a realistic scenario where:
		- Multiple edits to the same file (main.py)
		- Creating a new file (config.py)
		- Editing a different existing file (utils.py)
		- All operations should succeed and be applied correctly
		"""

		# Mock user confirmation to always return True
		async def mock_confirm(message, default):
			return True

		monkeypatch.setattr(edit_format_service, "prompt_for_confirmation", mock_confirm)

		# Create initial files with content
		main_content = "import sys\n\ndef main():\n	print('Hello')\n	return 0\n"
		utils_content = "def helper():\n	pass\n"

		main_file = create_test_file("src/main.py", main_content)
		utils_file = create_test_file("src/utils.py", utils_content)
		config_file = tmp_project_root / "src" / "config.py"  # Will be created

		# Content with multiple edits across multiple files
		content = dedent(f"""
		I'll make several changes across the project:

		1. First, let's add an import to main.py:
		```python
		+++++++ {main_file}
		<<<<<<< SEARCH
		import sys
		=======
		import sys
		import os
		>>>>>>> REPLACE
		```

		2. Now update the main() function in main.py:
		```python
		+++++++ {main_file}
		<<<<<<< SEARCH
		def main():
			print('Hello')
			return 0
		=======
		def main():
			print('Hello, World!')
			print(f"Running from: {{os.getcwd()}}")
			return 0
		>>>>>>> REPLACE
		```

		3. Create a new config.py file:
		```python
		+++++++ {config_file}
		<<<<<<< SEARCH
		=======
		DEBUG = True
		VERSION = "1.0.0"

		def get_config():
			return {{"debug": DEBUG, "version": VERSION}}
		>>>>>>> REPLACE
		```

		4. Update the helper function in utils.py:
		```python
		+++++++ {utils_file}
		<<<<<<< SEARCH
		def helper():
			pass
		=======
		def helper(data):
			\"\"\"Process data and return result.\"\"\"
			return data.upper()
		>>>>>>> REPLACE
		```
		""")

		blocks = await edit_format_service.handle(content)

		# Verify all blocks were processed
		assert len(blocks) == 4
		assert all(b.block_status == BlockStatus.VALID for b in blocks)

		# Verify block types
		main_blocks = [b for b in blocks if str(main_file) in b.file_path]
		config_blocks = [b for b in blocks if str(config_file) in b.file_path]
		utils_blocks = [b for b in blocks if str(utils_file) in b.file_path]

		assert len(main_blocks) == 2  # Two edits to main.py
		assert len(config_blocks) == 1  # One new file creation
		assert len(utils_blocks) == 1  # One edit to utils.py

		assert main_blocks[0].block_type == BlockType.EDIT
		assert main_blocks[1].block_type == BlockType.EDIT
		assert config_blocks[0].block_type == BlockType.ADD
		assert utils_blocks[0].block_type == BlockType.EDIT

		# Verify main.py has both changes applied
		final_main_content = main_file.read_text()
		assert "import sys" in final_main_content
		assert "import os" in final_main_content
		assert "Hello, World!" in final_main_content
		assert "Running from:" in final_main_content
		assert "os.getcwd()" in final_main_content

		# Verify config.py was created with correct content
		assert config_file.exists()
		final_config_content = config_file.read_text()
		assert "DEBUG = True" in final_config_content
		assert 'VERSION = "1.0.0"' in final_config_content
		assert "def get_config():" in final_config_content

		# Verify utils.py was updated
		final_utils_content = utils_file.read_text()
		assert "def helper(data):" in final_utils_content
		assert "Process data and return result" in final_utils_content
		assert "return data.upper()" in final_utils_content
		assert "pass" not in final_utils_content  # Old implementation removed
