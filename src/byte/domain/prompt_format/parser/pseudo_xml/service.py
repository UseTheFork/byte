import re
from pathlib import Path
from typing import List

from byte.domain.prompt_format.exceptions import NoBlocksFoundError, PreFlightCheckError
from byte.domain.prompt_format.parser.base import BaseParserService
from byte.domain.prompt_format.parser.pseudo_xml.prompt import edit_format_system, practice_messages
from byte.domain.prompt_format.schemas import (
    BlockType,
    EditFormatPrompts,
    SearchReplaceBlock,
)


class PseudoXmlParserService(BaseParserService):
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

    prompts: EditFormatPrompts
    edit_blocks: List[SearchReplaceBlock]

    async def boot(self):
        self.edit_blocks = []
        self.prompts = EditFormatPrompts(system=edit_format_system, examples=practice_messages)

    async def remove_blocks_from_content(self, content: str) -> str:
        """Remove pseudo-XML blocks from content and replace with summary message.

        Identifies all pseudo-XML file blocks in the content and replaces them with
        a concise message indicating changes were applied. Preserves any text
        outside of the blocks.

        Args:
                content: Content string containing pseudo-XML blocks

        Returns:
                str: Content with blocks replaced by summary messages

        Usage: `cleaned = service.remove_blocks_from_content(ai_response)`
        """
        # Pattern to match pseudo-XML file blocks
        pattern = r'<file\s+path="([^"]+)"\s+operation="([^"]+)"\s*>\s*<search>(.*?)</search>\s*<replace>(.*?)</replace>\s*</file>'

        def replacement(match):
            file_path = match.group(1)
            return f"*[Changes applied to `{file_path.strip()}` - block removed]*"

        # Replace all blocks with summary messages
        cleaned_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return cleaned_content

    async def parse_content_to_blocks(self, content: str) -> List[SearchReplaceBlock]:
        """Extract SEARCH/REPLACE blocks from AI response content.

        Parses pseudo-XML blocks containing file operations with search/replace content.
        Handles empty search/replace sections gracefully.

        Args:
                content: Raw content string containing pseudo-XML blocks

        Returns:
                List of SearchReplaceBlock objects parsed from the content

        Usage: `blocks = service.parse_content_to_blocks(ai_response)`
        """

        blocks = []

        # Pattern to match pseudo-XML file blocks with search/replace content
        # <file path="..." operation="...">
        #   <search>...</search>
        #   <replace>...</replace>
        # </file>
        pattern = r'<file\s+path="([^"]+)"\s+operation="([^"]+)"\s*>\s*<search>(.*?)</search>\s*<replace>(.*?)</replace>\s*</file>'

        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            file_path, operation, search_content, replace_content = match

            # Strip leading/trailing whitespace but preserve internal structure
            search_content = search_content.strip()
            replace_content = replace_content.strip()

            # Determine block type based on operation and file existence
            file_path_obj = Path(file_path.strip())
            if not file_path_obj.is_absolute() and self._config and self._config.project_root:
                file_path_obj = (self._config.project_root / file_path_obj).resolve()
            else:
                file_path_obj = file_path_obj.resolve()

            # Map operation string to BlockType
            if operation == "delete":
                block_type = BlockType.REMOVE
            elif operation == "replace":
                block_type = BlockType.REPLACE
            elif operation == "create":
                block_type = BlockType.ADD
            elif operation == "edit":
                block_type = BlockType.EDIT
            else:
                # Default to EDIT for unknown operations
                block_type = BlockType.EDIT

            blocks.append(
                SearchReplaceBlock(
                    file_path=file_path.strip(),
                    search_content=search_content,
                    replace_content=replace_content,
                    block_type=block_type,
                )
            )
        return blocks

    async def pre_flight_check(self, content: str) -> None:
        """Validate that pseudo-XML block markers are properly balanced.

        Counts occurrences of required XML tags and raises an exception
        if they don't match, indicating malformed blocks.
        """
        file_open_count = len(re.findall(r'<file\s+path="[^"]+"\s+operation="[^"]+"', content))
        file_close_count = content.count("</file>")
        search_count = content.count("<search>")
        search_close_count = content.count("</search>")
        replace_count = content.count("<replace>")
        replace_close_count = content.count("</replace>")

        if file_open_count == 0:
            raise NoBlocksFoundError(
                "No pseudo-XML file blocks found in content. AI responses must include properly formatted edit blocks."
            )

        if file_open_count != file_close_count:
            raise PreFlightCheckError(
                f"Malformed pseudo-XML blocks: "
                f"<file> tags={file_open_count}, </file> tags={file_close_count}. "
                f"Opening and closing tags must match."
            )

        if search_count != search_close_count:
            raise PreFlightCheckError(
                f"Malformed pseudo-XML blocks: "
                f"<search> tags={search_count}, </search> tags={search_close_count}. "
                f"Opening and closing tags must match."
            )

        if replace_count != replace_close_count:
            raise PreFlightCheckError(
                f"Malformed pseudo-XML blocks: "
                f"<replace> tags={replace_count}, </replace> tags={replace_close_count}. "
                f"Opening and closing tags must match."
            )

        if search_count != replace_count:
            raise PreFlightCheckError(
                f"Malformed pseudo-XML blocks: "
                f"<search> tags={search_count}, <replace> tags={replace_count}. "
                f"Each file block must have matching search and replace tags."
            )
