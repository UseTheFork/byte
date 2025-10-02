import re
from pathlib import Path
from typing import Optional, Set

from watchfiles import Change, awatch

from byte.core.event_bus import Payload
from byte.core.logging import log
from byte.core.service.base_service import Service
from byte.core.task_manager import TaskManager
from byte.domain.agent.implementations.ask.agent import AskAgent
from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.cli.service.prompt_toolkit_service import PromptToolkitService
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService


class FileWatcherService(Service):
    """Simple file watcher service using TaskManager for background monitoring.

    Watches project files for changes and AI comment patterns.
    Usage: Automatically started during boot to monitor file changes
    """

    async def boot(self) -> None:
        """Initialize file watcher with TaskManager integration."""
        self._watched_files: Set[Path] = set()
        self.task_manager = await self.make(TaskManager)

        self._ai_patterns = [
            re.compile(r"//.*?AI([:|@])\s*(.*)$", re.MULTILINE | re.IGNORECASE),
            re.compile(r"#.*?AI([:|@])\s*(.*)$", re.MULTILINE | re.IGNORECASE),
            re.compile(r"--.*?AI([:|@])\s*(.*)$", re.MULTILINE | re.IGNORECASE),
            re.compile(
                r"<!--.*?AI([:|@])\s*(.*?)\s*-->",
                re.MULTILINE | re.DOTALL | re.IGNORECASE,
            ),
        ]

        await self._start_watching()

    async def _start_watching(self) -> None:
        """Start file system monitoring using TaskManager."""
        if not self._config.project_root or not self._config.project_root.exists():
            return

        # Get files to watch
        file_discovery = await self.make(FileDiscoveryService)
        discovered_files = await file_discovery.get_files()
        self._watched_files = set(discovered_files)

        # Start watching with TaskManager
        self.task_manager.start_task("file_watcher", self._watch_files())

    async def _watch_files(self) -> None:
        """Main file watching loop."""
        try:
            async for changes in awatch(str(self._config.project_root)):
                for change_type, file_path_str in changes:
                    file_path = Path(file_path_str)
                    await self._handle_file_change(file_path, change_type)
        except Exception as e:
            print(f"File watcher error: {e}")

    async def _handle_file_change(self, file_path: Path, change_type: Change) -> None:
        """Handle file system changes."""

        # Skip directory changes - we only want to monitor file changes
        if file_path.is_dir():
            return

        file_discovery_service = await self.make(FileDiscoveryService)

        # Skip if file is ignored by gitignore patterns
        if await file_discovery_service._is_ignored(file_path):
            return

        result = False
        if change_type == Change.deleted:
            self._watched_files.discard(file_path)
            file_service = await self.make(FileService)
            if await file_service.is_file_in_context(file_path):
                result = await file_service.remove_file(file_path)
        elif change_type in [Change.added, Change.modified]:
            result = await self._handle_file_modified(file_path)

        if result:
            prompt_toolkit_service = await self.make(PromptToolkitService)
            await prompt_toolkit_service.interrupt()

    async def _handle_file_modified(self, file_path: Path) -> bool:
        """Handle file modification by scanning for AI comments."""
        try:
            content = file_path.read_text(encoding="utf-8")
            ai_result = await self._scan_for_ai_comments(file_path, content)

            if ai_result:
                # Use the determined file mode from the scan result
                file_mode = ai_result["file_mode"]
                auto_add_result = await self._auto_add_file_to_context(
                    file_path, file_mode
                )

                log.info(ai_result)

                # Return true if file was added OR if there's an action type
                return auto_add_result or ai_result.get("action_type") is not None

            return False
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            return False

    async def _scan_for_ai_comments(
        self, file_path: Path, content: str
    ) -> Optional[dict]:
        """Scan file content for AI comment patterns.

        Returns dict with line_nums, comments, and action_type, or None if no AI comments found.
        """
        line_nums = []
        comments = []
        action_type = None
        file_mode = FileMode.EDITABLE  # Default to editable

        # Scan each line for AI comment patterns
        for i, line in enumerate(content.splitlines(), 1):
            # Check each pattern against the current line
            for pattern in self._ai_patterns:  # Use the plural version
                if match := pattern.search(line):
                    comment_text = match.group(0).strip()
                    ai_marker = match.group(1) if match.groups() else ":"

                    if comment_text:
                        line_nums.append(i)
                        comments.append(comment_text)

                        # Determine file mode based on AI marker
                        if ai_marker == "@":
                            file_mode = FileMode.READ_ONLY
                        elif ai_marker == ":":
                            file_mode = FileMode.EDITABLE

                        # Check the actual comment content for action markers
                        comment = comment_text.lower()
                        comment = comment.lstrip("/#-;").strip()
                        if comment.startswith("ai!") or comment.endswith("ai!"):
                            action_type = "!"
                        elif comment.startswith("ai?") or comment.endswith("ai?"):
                            action_type = "?"

                    # break  # Found match on this line, no need to check other patterns

        # Return None if no AI comments found
        if not line_nums:
            return None

        return {
            "line_nums": line_nums,
            "comments": comments,
            "action_type": action_type,
            "file_mode": file_mode,
            "file_path": file_path,
        }

    async def _auto_add_file_to_context(
        self, file_path: Path, mode: FileMode = FileMode.EDITABLE
    ) -> bool:
        """Automatically add file to context when AI comment is detected."""
        file_service = await self.make(FileService)
        return await file_service.add_file(file_path, mode)

    def get_watched_files(self) -> Set[Path]:
        """Get the current set of files being watched."""
        return self._watched_files.copy()

    async def scan_context_files_for_ai_comments(self) -> Optional[dict]:
        """Scan all files currently in context for AI comment patterns.

        Returns a dict with prompt and agent info for the first AI comment found, or None if no triggers found.
        """
        file_service = await self.make(FileService)
        context_files = file_service.list_files()  # Get all files in context
        gathered_comments = []

        for file_context in context_files:
            content = file_context.get_content()
            if not content:
                continue

            result = await self._scan_for_ai_comments(file_context.path, content)
            if result:
                gathered_comments.append(result)

        # From https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/watch_prompts.py#L6

        if not gathered_comments:
            return None

        # Process the first AI comment found (prioritize by action type)
        urgent_comments = [c for c in gathered_comments if c.get("action_type") == "!"]
        question_comments = [
            c for c in gathered_comments if c.get("action_type") == "?"
        ]
        regular_comments = [
            c for c in gathered_comments if c.get("action_type") not in ["!", "?"]
        ]

        # Prioritize urgent (!) comments first, then questions (?), then regular
        target_comment = None
        if urgent_comments:
            target_comment = urgent_comments[0]
        elif question_comments:
            target_comment = question_comments[0]
        elif regular_comments:
            target_comment = regular_comments[0]

        if target_comment:
            action_type = target_comment.get("action_type")
            # TODO: we should prob do somthing with this.
            # comments_text = " ".join(target_comment.get("comments", []))

            # Extract instruction from the comment text
            ai_instruction = ""
            for comment in target_comment.get("comments", []):
                # Remove comment markers and extract instruction
                clean_comment = comment.lower().strip()
                clean_comment = clean_comment.lstrip("/#-;").strip()
                if clean_comment.startswith("ai"):
                    ai_instruction = clean_comment[2:].lstrip(":@!?").strip()
                    break

            if action_type == "!":
                # Urgent task - use standard watch prompt with CoderAgent
                return {
                    "prompt": """I've written your instructions in comments in the code and marked them with "AI"
                    Find them in the code files I've shared with you, and follow their instructions.

                    **IMPORTANT**: After completing those instructions, also be sure to remove all the "AI" comments from the code too.""",
                    "agent_type": CoderAgent,
                    "ai_instruction": ai_instruction,
                }
            elif action_type == "?":
                # Question - modify prompt to answer the question
                return {
                    "prompt": """I've written a question in the code comments that needs to be answered.

                    Provide a clear, concise, helpful answer based on the code context.""",
                    "agent_type": AskAgent,
                    "ai_instruction": ai_instruction,
                }
            else:
                return None

        return None

    async def modify_user_request(self, payload: Optional[Payload] = None):
        if payload:
            interrupted = payload.get("interrupted", False)
            user_input = payload.get("user_input", "")
            if interrupted and user_input is None:
                # Scan context files for AI comments
                ai_result = await self.scan_context_files_for_ai_comments()

                if ai_result:
                    payload = payload.set("user_input", ai_result["prompt"])
                    payload = payload.set("interrupted", False)
                    payload = payload.set("active_agent", ai_result["agent_type"])

        return payload
