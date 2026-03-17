from __future__ import annotations

import re

from byte.code_operations import BlockType
from byte.code_operations.blocks.file.base_file_operation_block import BaseFileOperationBlock
from byte.code_operations.schemas import BlockStatus
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text


class EditFileOperationBlock(BaseFileOperationBlock):
    """Represents parsed edit operation block."""

    def _check_single_block_tags_balanced(self, raw_content: str) -> tuple[bool, str]:
        """Validate that search/replace tags are balanced in a single block.

        Returns:
            Tuple of (is_valid, error_message)

        Usage: `valid, error = self._check_single_block_tags_balanced(content)`
        Usage: `valid, error = self._check_single_block_tags_balanced(content)`
        """
        search_count = raw_content.count(Boundary.open(BoundaryType.SEARCH))
        search_close_count = raw_content.count(Boundary.close(BoundaryType.SEARCH))
        replace_count = raw_content.count(Boundary.open(BoundaryType.REPLACE))
        replace_close_count = raw_content.count(Boundary.close(BoundaryType.REPLACE))

        if search_count != search_close_count:
            return (
                False,
                list_to_multiline_text(
                    [
                        "Unbalanced tags: Open and close tag counts must be equal",
                        f"{Boundary.open(BoundaryType.SEARCH)} tags={search_count}",
                        f"{Boundary.close(BoundaryType.SEARCH)} tags={search_close_count}",
                    ]
                ),
            )

        if replace_count != replace_close_count:
            return (
                False,
                list_to_multiline_text(
                    [
                        "Unbalanced tags: Open and close tag counts must be equal",
                        f"{Boundary.open(BoundaryType.REPLACE)} tags={replace_count}",
                        f"{Boundary.close(BoundaryType.REPLACE)} tags={replace_close_count}",
                    ]
                ),
            )

        if search_count != replace_count:
            return (
                False,
                list_to_multiline_text(
                    [
                        "Unbalanced tags: Search and replace tag counts must be equal",
                        f"{Boundary.open(BoundaryType.SEARCH)} tags={search_count}",
                        f"{Boundary.open(BoundaryType.REPLACE)} tags={replace_count}",
                    ]
                ),
            )

        return True, ""

    def _find_search_content_in_file(
        self, search_content: str, replace_content: str, file_content: str
    ) -> tuple[bool, str, str]:
        """Try to find search content in file with progressive fallback strategies.

        Attempts to locate the search content in the file using multiple strategies:
        1. Exact match (no modifications)
        2. Match after stripping leading/trailing newlines
        3. Match after stripping all leading/trailing whitespace

        Args:
            search_content: The content to search for in the file
            replace_content: The replacement content (will be stripped if search is stripped)
            file_content: The full content of the file to search in

        Returns:
            Tuple of (found, matched_search_content, matched_replace_content)
            - found: True if content was found, False otherwise
            - matched_search_content: The search content that matched (potentially stripped)
            - matched_replace_content: The replace content (stripped if search was stripped)

        Usage: `found, search, replace = self._find_search_content_in_file(search, replace, content)`
        """

        # First try exact match without any stripping
        if search_content and search_content in file_content:
            self.app["log"].debug("Found exact match (no stripping)")
            return True, search_content, replace_content

        # Try stripping newlines as a fallback
        newline_stripped_search = search_content.strip("\n")
        if newline_stripped_search and newline_stripped_search in file_content:
            self.app["log"].debug("Found match after stripping newlines")
            return True, newline_stripped_search, replace_content.strip("\n")

        # Try stripping all whitespace as a fallback
        stripped_search = search_content.strip()
        if stripped_search and stripped_search in file_content:
            self.app["log"].debug("Found match after stripping all whitespace")
            return True, stripped_search, replace_content.strip()

        # No match found with any strategy
        self.app["log"].debug("No match found with any strategy")
        self.app["log"].debug(f"Search content attempted:\n{search_content}")
        return False, search_content, replace_content

    def _extract_search_replace_content(self, raw_content: str) -> tuple[str, str]:
        """Extract search and replace content from raw edit block content.

        Args:
            raw_content: Raw content string containing search/replace pseudo-XML tags

        Returns:
            Tuple of (search_content, replace_content)

        Usage: `search, replace = self._extract_search_replace_content(raw_content)`
        """
        # Extract search content
        search_pattern = rf"<{BoundaryType.SEARCH}>(.*?)</{BoundaryType.SEARCH}>"
        search_match = re.search(search_pattern, raw_content, re.DOTALL)
        search_content = search_match.group(1) if search_match else ""

        # Extract replace content
        replace_pattern = rf"<{BoundaryType.REPLACE}>(.*?)</{BoundaryType.REPLACE}>"
        replace_match = re.search(replace_pattern, raw_content, re.DOTALL)
        replace_content = replace_match.group(1) if replace_match else ""

        return search_content, replace_content

    def prepare(self) -> tuple[BlockStatus, str]:
        """Prepare the edit block by validating constraints and loading necessary content.

        Returns:
            Tuple of (status, error_message). BlockStatus.VALID if valid, appropriate error status  otherwise.

        Usage: `status, error = block.prepare()` -> (BlockStatus.VALID, "") or (BlockStatus.PARSE_ERROR, "error message")
        """
        # First check if tags are balanced
        is_valid, error_msg = self._check_single_block_tags_balanced(self.raw_content)
        if not is_valid:
            return BlockStatus.INVALID, error_msg

        # Extract search and replace content
        search_content, replace_content = self._extract_search_replace_content(self.raw_content)

        # Read file content to validate search content exists
        try:
            file_content = self.resolved_file_path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            return BlockStatus.INVALID, f"Cannot read file: {self.file_path} - {e!s}"

        # Try to find search content in file
        found, matched_search, matched_replace = self._find_search_content_in_file(
            search_content,
            replace_content,
            file_content,
        )

        if not found:
            return (
                BlockStatus.INVALID,
                f"Search content not found in `{self.file_path}`.\n\nCurrent File Content:\n```\n{file_content}\n```",
            )

        # Set the matched content on self
        self.search_content = matched_search
        self.content = matched_replace

        return BlockStatus.VALID, ""

    def to_block_format(self) -> str:
        """Format block as a structured block string.

        Returns:
            str: Formatted block string

        Usage: `formatted = block.to_block_format()` -> formatted block string
        """

        sections = [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": self.file_path, "operation": BlockType.EDIT, "block_id": self.block_id},
            ),
            Boundary.open(BoundaryType.SEARCH),
            self.search_content,
            Boundary.close(BoundaryType.SEARCH),
            Boundary.open(BoundaryType.REPLACE),
            self.content,
            Boundary.close(BoundaryType.REPLACE),
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]

        return list_to_multiline_text(sections)

    def to_error_format(self) -> str:
        """Format block as an error message for LLM feedback.

        Returns:
            str: Formatted error block string with status information

        Usage: `error_msg = block.to_error_format()` -> formatted error block
        """

        sections = [
            Boundary.open(BoundaryType.ERROR, meta={"operation": BlockType.EDIT, "block_id": str(self.block_id)}),
            f"**File:** `{self.file_path}`",
            f"**Status:** {self.status.value}",
            f"**Issue:**\n{self.status_message}",
            Boundary.close(BoundaryType.ERROR),
        ]

        return list_to_multiline_text(sections)

    async def apply(self):
        """Apply the edit operation to the file system.

        Replaces the first occurrence of search content with replace content in the file.
        If search content is empty, appends replace content to the end of the file.

        Returns:
            Tuple of (status, error_message). BlockStatus.APPLIED if successful,
            appropriate error status otherwise with error message.

        Usage: `status, error = block.apply()` -> (BlockStatus.APPLIED, "") or (BlockStatus.INVALID, "error message")
        """
        try:
            content = self.resolved_file_path.read_text(encoding="utf-8")

            # Handle empty search content (append to file)
            if not self.search_content:
                new_content = content + self.content
            else:
                # Replace first occurrence of search content
                new_content = content.replace(
                    self.search_content,
                    self.content,
                    1,  # Only replace first occurrence
                )

            self.resolved_file_path.write_text(new_content, encoding="utf-8")

            self.status = BlockStatus.APPLIED

        except (PermissionError, OSError, UnicodeDecodeError, UnicodeEncodeError) as e:
            self.status = BlockStatus.INVALID
            self.status_message = f"Operation Failed: {e!s}"

    def to_dict(self) -> dict:
        """Serialize edit block to dictionary."""
        data = super().to_dict()
        data["search_content"] = self.search_content if hasattr(self, "search_content") else ""
        data["content"] = self.content if hasattr(self, "content") else ""
        return data
