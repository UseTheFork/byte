import re
from pathlib import Path
from textwrap import dedent
from typing import List, Optional, Set

from watchfiles import Change, awatch

from byte.core.event_bus import Payload
from byte.core.service.base_service import Service
from byte.core.task_manager import TaskManager
from byte.domain.agent.implementations.ask.agent import AskAgent
from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.cli.service.prompt_toolkit_service import PromptToolkitService
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService
from byte.domain.files.service.ignore_service import FileIgnoreService


class FileWatcherService(Service):
	"""Simple file watcher service using TaskManager for background monitoring.

	Watches project files for changes and AI comment patterns.
	Usage: Automatically started during boot to monitor file changes
	"""

	async def boot(self) -> None:
		"""Initialize file watcher with TaskManager integration."""
		self._watched_files: Set[Path] = set()
		self.task_manager = await self.make(TaskManager)
		self.ignore_service = await self.make(FileIgnoreService)
		await self._start_watching()

	async def _is_ignored(self, path: Path) -> bool:
		"""Check if a path should be ignored using FileIgnoreService."""
		ignore_service = await self.make(FileIgnoreService)
		return await ignore_service.is_ignored(path)

	def _watch_filter(self, change: Change, path: str) -> bool:
		"""Filter function for watchfiles to ignore files based on ignore patterns.

		NOTE: This is a synchronous filter function required by watchfiles library.
		We cache the ignore service's pathspec for efficient synchronous filtering.
		Usage: Used internally by awatch to determine which file changes to process.
		"""
		if not self._config.project_root:
			return True

		try:
			# Get the cached pathspec from ignore service
			# This is safe because _start_watching ensures ignore service is booted
			spec = self.ignore_service.get_pathspec()

			if not spec:
				return True

			file_path = Path(path)
			relative_path = file_path.relative_to(self._config.project_root)

			# Check both file and directory patterns
			is_ignored = spec.match_file(str(relative_path)) or spec.match_file(str(relative_path) + "/")

			# Return True to include the file (i.e., not ignored)
			return not is_ignored
		except (ValueError, RuntimeError):
			# Path is outside project root or async error, ignore it
			return False

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
			async for changes in awatch(str(self._config.project_root), watch_filter=self._watch_filter):
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

		result = False
		if change_type == Change.deleted:
			# Remove from both watcher and discovery caches
			self._watched_files.discard(file_path)
			await file_discovery_service.remove_file(file_path)

			file_service = await self.make(FileService)
			if await file_service.is_file_in_context(file_path):
				result = await file_service.remove_file(file_path)
		elif change_type == Change.added:
			# Add to discovery cache if not ignored
			added = await file_discovery_service.add_file(file_path)
			if added:
				self._watched_files.add(file_path)
				result = await self._handle_file_modified(file_path)
		elif change_type == Change.modified:
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
				auto_add_result = await self._auto_add_file_to_context(file_path, file_mode)

				# Return true if file was added OR if any AI comments were found
				return auto_add_result or bool(ai_result.get("action_type"))

			return False
		except (FileNotFoundError, PermissionError, UnicodeDecodeError):
			return False

	async def _scan_for_ai_comments(self, file_path: Path, content: str) -> Optional[dict]:
		"""Scan file content for AI comment patterns.

		Returns dict with line_nums, comments, and action_type, or None if no AI comments found.
		"""
		comments = []
		action_type = None
		file_mode = FileMode.EDITABLE

		# First pass: Extract all comment lines
		comment_blocks = self._extract_comment_lines(content)

		# Second pass: Check extracted comments for AI markers
		for comment_block in comment_blocks:
			ai_match = self._check_for_ai_marker(comment_block)

			if ai_match:
				comments.append(comment_block)

				# Determine file mode based on AI marker
				if ai_match["marker"] == "@":
					file_mode = FileMode.READ_ONLY
				elif ai_match["marker"] == ":":
					file_mode = FileMode.EDITABLE

				# Track action type (prioritize ! over ?)
				if ai_match["action"] == "!":
					action_type = "!"
				elif ai_match["action"] == "?" and action_type != "!":
					action_type = "?"

		if not comments:
			return None

		return {
			"comments": comments,
			"action_type": action_type,
			"file_mode": file_mode,
			"file_path": file_path,
		}

	def _extract_comment_lines(self, content: str) -> List[str]:
		"""Extract comment blocks from content.

		A comment block is one or more consecutive lines starting with a comment marker.
		Returns list of (starting_line_number, combined_comment_text) tuples.
		"""
		comment_blocks = []

		# Common single-line comment patterns across languages
		single_line_markers = ["#", "//", "--", ";", "%"]

		current_block = []

		for i, line in enumerate(content.splitlines(), 1):
			stripped_line = line.strip()

			# Check if line starts with any comment marker
			is_comment = any(stripped_line.startswith(marker) for marker in single_line_markers)

			if is_comment:
				# Start or continue a comment block
				current_block.append(stripped_line)
			else:
				# Non-comment line - end current block if one exists
				if current_block:
					combined_text = "\n".join(current_block)
					comment_blocks.append(combined_text)
					current_block = []

		# Don't forget the last block if file ends with comments
		if current_block:
			combined_text = "\n".join(current_block)
			comment_blocks.append(combined_text)

		return comment_blocks

	def _check_for_ai_marker(self, comment_text: str) -> Optional[dict]:
		"""Check if a comment contains an AI marker.

		Returns dict with marker and action type, or None if no AI marker found.
		"""

		# Pattern to find "AI" followed by a marker (case-insensitive)
		ai_pattern = re.compile(r"\bAI([:|@!?])", re.IGNORECASE)
		match = ai_pattern.search(comment_text)

		if not match:
			return None

		marker_char = match.group(1)

		# Determine the marker type (: or @)
		marker = "@" if marker_char == "@" else ":"

		# Determine action type (! or ?)
		action = None
		comment_text = comment_text.lower().strip()
		if comment_text.endswith("ai!"):
			action = "!"
		elif comment_text.endswith("ai?"):
			action = "?"

		return {"marker": marker, "action": action}

	async def _auto_add_file_to_context(self, file_path: Path, mode: FileMode = FileMode.EDITABLE) -> bool:
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
		action_type = None
		ai_instruction = []

		for file_context in context_files:
			content = file_context.get_content()
			if not content:
				continue

			result = await self._scan_for_ai_comments(file_context.path, content)

			if result:
				# Track action type (prioritize ! over ?)
				if result["action_type"] == "!":
					action_type = "!"
				elif result["action_type"] == "?" and action_type != "!":
					action_type = "?"

				gathered_comments.append(result)

		if not gathered_comments:
			return None

		for single_comment in gathered_comments:
			comment_action_type = single_comment.get("action_type")

			# Only include comments based on the action type
			if action_type == comment_action_type:
				file_path = single_comment.get("file_path")

				ai_instruction.append(f"## File: {file_path}")
				ai_instruction.append("### Comments")

				# Extract instruction from the comment text
				for comment in single_comment.get("comments", []):
					# Remove comment markers and extract instruction
					clean_comment = comment.strip().lstrip("/#-;").strip()
					ai_instruction.append(f"{clean_comment.strip()}\n")

		ai_instruction = "\n".join(ai_instruction)

		# Credits to https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/watch_prompts.py#L6

		if action_type == "!":
			# Urgent task - use standard watch prompt with CoderAgent
			return {
				"prompt": dedent(f"""
				# Task
				I've written task instructions in code comments marked with "AI:".

				# Extracted instructions:
				{ai_instruction}

				> **IMPORTANT**: Execute these instructions following the project's coding standards and conventions. If multiple tasks are present, complete them in the order they appear. After successfully implementing all changes, remove the "AI:" comment markers from the code."""),
				"agent_type": CoderAgent,
			}
		elif action_type == "?":
			# Question - modify prompt to answer the question
			return {
				"prompt": dedent(f"""
				I've written questions in code comments marked with "AI:".

				Extracted questions:
				{ai_instruction}

				Provide clear, well-structured answers based on the code context. Include:
				- Direct answer to each question
				- Relevant code examples or references when applicable
				- Recommendations or best practices if appropriate"

				Provide a clear, concise, helpful answer based on the code context."""),
				"agent_type": AskAgent,
			}
		else:
			return None

	async def modify_user_request_hook(self, payload: Optional[Payload] = None):
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
