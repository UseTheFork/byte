import re

from langchain_core.messages import BaseMessage

from byte import Service
from byte.clipboard.schemas import CodeBlock
from byte.prompt_format import SearchReplaceBlock
from byte.support.utils import extract_content_from_message, get_language_from_filename


class ClipboardService(Service):
    """Service for managing extracted code blocks from AI messages.

    Maintains a session-scoped collection of code blocks that can be
    copied to clipboard on demand.
    Usage: `service = app.make(ClipboardService)`
    """

    def boot(self):
        """Initialize the clipboard service with an empty store.

        Usage: `service = ClipboardService(container)`
        """
        self.code_blocks = []

    def _extract_code_blocks(self, content: str) -> list[CodeBlock]:
        """Extract all code blocks from content with their language identifiers.

        Args:
            content: Text content containing code blocks

        Returns:
            List of CodeBlock instances

        Usage: `blocks = self._extract_code_blocks(message_text)`
        """
        # Pattern to match code blocks: ```language\ncontent\n```
        pattern = r"```(\w*)\n(.*?)```"
        matches = re.findall(pattern, content, re.DOTALL)

        blocks = []
        for language, code_content in matches:
            # Use "text" as default language if not specified
            lang = language if language else "text"
            blocks.append(CodeBlock(language=lang, content=code_content.strip()))

        return blocks

    async def extract_from_message(self, message: BaseMessage):
        """Extract code blocks from a message and store them in the session context.

        Parses markdown code blocks from the message content and converts them
        into CodeBlock instances with language detection.

        Usage: `await service.extract_from_message(last_message)`
        """
        content = extract_content_from_message(message)
        code_blocks = self._extract_code_blocks(content)
        self.code_blocks.extend(code_blocks)

    # AI: update the doc string ai!
    async def extract_from_blocks(self, parsed_blocks: list[SearchReplaceBlock]):
        """Extract code blocks from parsed SearchReplaceBlock instances and store them.

        Converts each block's replace_content into a CodeBlock with language detection
        based on the file path extension.

        Usage: `await service.extract_from_blocks(parsed_blocks)`
        """

        for block in parsed_blocks:
            language = get_language_from_filename(block.file_path)
            if language is None:
                language = "text"

            code_block = CodeBlock(
                language=language,
                content=block.replace_content,
            )
            self.code_blocks.append(code_block)

    def get_code_blocks(self) -> list[CodeBlock]:
        """Get all stored code blocks from the session.

        Usage: `blocks = service.get_code_blocks()`
        """
        return self.code_blocks
