import re
from pathlib import Path
from typing import List

from byte.domain.edit_format.exceptions import NoBlocksFoundError, PreFlightCheckError
from byte.domain.edit_format.parser.base import BaseParserService
from byte.domain.edit_format.parser.search_replace.prompt import edit_format_system, practice_messages
from byte.domain.edit_format.schemas import (
    BlockType,
    EditFormatPrompts,
    SearchReplaceBlock,
)


class SearchReplaceBlockParserService(BaseParserService):
    """Service for parsing, validating, and applying SEARCH/REPLACE edit blocks from AI responses.

    Handles the complete lifecycle of code modifications proposed by AI agents:
    - Parses SEARCH/REPLACE blocks from markdown-formatted responses
    - Validates blocks against file permissions, existence, and content
    - Applies file operations (create, edit, delete) with user confirmation
    - Integrates with file context to respect read-only constraints
    - Removes applied blocks from historic messages to reduce token usage

    Usage: `blocks = await service.handle(ai_response)` -> parses, validates, and applies all blocks
    Usage: `cleaned = service.remove_blocks_from_content(content)` -> strips blocks from text
    """

    add_file_marker: str = "+++++++"
    remove_file_marker: str = "-------"
    search: str = "<<<<<<< SEARCH"
    divider: str = "======="
    replace: str = ">>>>>>> REPLACE"

    prompts: EditFormatPrompts
    edit_blocks: List[SearchReplaceBlock]

    async def boot(self):
        self.edit_blocks = []
        self.prompts = EditFormatPrompts(system=edit_format_system, examples=practice_messages)

    async def parse_content_to_blocks(self, content: str) -> List[SearchReplaceBlock]:
        """Extract SEARCH/REPLACE blocks from AI response content.

        Parses code fence blocks containing SEARCH/REPLACE markers and extracts
        the operation type, file path, search content, and replacement content.
        Handles empty search/replace sections gracefully.

        Args:
                content: Raw content string containing SEARCH/REPLACE blocks

        Returns:
                List of SearchReplaceBlock objects parsed from the content

        Usage: `blocks = service.parse_content_to_blocks(ai_response)`
        """

        blocks = []

        # Pattern to match the entire SEARCH/REPLACE block structure
        # The (.*?) captures allow for empty content between markers
        pattern = r"```\w*\n(\+\+\+\+\+\+\+|-------) (.+?)\n<<<<<<<SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE\n```"

        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            operation, file_path, search_content, replace_content = match

            # Strip leading/trailing newlines from search and replace content
            # This handles cases where empty sections have extra newlines
            search_content = search_content.rstrip("\n").lstrip("\n")
            replace_content = replace_content.rstrip("\n").lstrip("\n")

            # Determine block type based on operation and content
            file_path_obj = Path(file_path.strip())
            if not file_path_obj.is_absolute() and self._config and self._config.project_root:
                file_path_obj = (self._config.project_root / file_path_obj).resolve()
            else:
                file_path_obj = file_path_obj.resolve()

            if operation == self.remove_file_marker:
                # --- operation: remove file or replace entire contents
                if search_content == "" and replace_content == "":
                    block_type = BlockType.REMOVE
                elif file_path_obj.exists() and search_content == "":
                    # Replace entire file contents when search is empty
                    block_type = BlockType.REPLACE
                elif file_path_obj.exists():
                    block_type = BlockType.EDIT
                else:
                    block_type = BlockType.ADD
            else:  # +++ operation
                # +++ operation: edit existing or create new
                if file_path_obj.exists():
                    block_type = BlockType.EDIT
                else:
                    block_type = BlockType.ADD

            blocks.append(
                SearchReplaceBlock(
                    file_path=file_path.strip(),
                    search_content=search_content,
                    replace_content=replace_content,
                    block_type=block_type,
                )
            )
        return blocks

    def remove_blocks_from_content(self, content: str) -> str:
        """Remove SEARCH/REPLACE blocks from content and replace with summary message.

        Identifies all search/replace blocks in the content and replaces them with
        a concise message indicating changes were applied. Preserves any text
        outside of the blocks.

        Args:
                content: Content string containing search/replace blocks

        Returns:
                str: Content with blocks replaced by summary messages

        Usage: `cleaned = service.remove_blocks_from_content(ai_response)`
        """
        # Pattern to match the entire SEARCH/REPLACE block structure
        pattern = r"```\w*\n(\+\+\+\+\+\+\+|-------) (.+?)\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE\n```"

        def replacement(match):
            _, file_path, _, _ = match.groups()

            return f"*[Changes applied to `{file_path.strip()}` - search/replace block removed]*"

        # Replace all blocks with summary messages
        cleaned_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return cleaned_content

    async def pre_flight_check(self, content: str) -> None:
        """Validate that SEARCH/REPLACE block markers are properly balanced.

        Counts occurrences of all five required markers and raises an exception
        if they don't match, indicating malformed blocks.
        """
        search_count = content.count(self.search)
        replace_count = content.count(self.replace)
        divider_count = content.count(self.divider)
        file_marker_count = content.count(self.add_file_marker) + content.count(self.remove_file_marker)

        if search_count == 0 and replace_count == 0 and divider_count == 0 and file_marker_count == 0:
            raise NoBlocksFoundError(
                "No SEARCH/REPLACE blocks found in content. AI responses must include properly formatted edit blocks."
            )

        if not (search_count == replace_count == divider_count == file_marker_count):
            raise PreFlightCheckError(
                f"Malformed SEARCH/REPLACE blocks: "
                f"SEARCH={search_count}, REPLACE={replace_count}, "
                f"dividers={divider_count}, file markers={file_marker_count}. "
                f"All counts must be equal."
            )
