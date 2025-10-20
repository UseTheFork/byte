from typing import List

from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.schemas import FileMode
from byte.domain.files.service.file_service import FileService


class AddFileCommand(Command):
	"""Command to add files to AI context as editable.

	Enables users to make files available for AI modification via
	SEARCH/REPLACE blocks, with intelligent tab completion from project files.
	Usage: `/add main.py` -> file becomes editable in AI context
	"""

	@property
	def name(self) -> str:
		return "add"

	@property
	def description(self) -> str:
		return "Add file to context as editable"

	async def execute(self, args: str) -> None:
		"""Add specified file to context with editable permissions."""
		console = await self.make(ConsoleService)

		if not args:
			console.print("Usage: /add <file_path>")
			return

		file_service = await self.make(FileService)
		result = await file_service.add_file(args, FileMode.EDITABLE)

		if not result:
			console.print(
				f"[error]Failed to add {args} (file not found, not readable, or is already in context)[/error]"
			)

	async def get_completions(self, text: str) -> List[str]:
		"""Provide intelligent file path completions from project discovery.

		Uses the file discovery service to suggest project files that match
		the input pattern, respecting gitignore patterns automatically.
		"""
		try:
			file_service = await self.make(FileService)

			# Get project files matching the pattern
			matches = await file_service.find_project_files(text)

			# Filter out files already in context to avoid duplicates
			return [f for f in matches if not await file_service.is_file_in_context(f)]
		except Exception:
			# Fallback to empty list if discovery fails
			return []
