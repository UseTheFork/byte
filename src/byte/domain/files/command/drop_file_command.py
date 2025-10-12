from typing import List

from rich.console import Console

from byte.domain.cli.service.command_registry import Command
from byte.domain.files.service.file_service import FileService


class DropFileCommand(Command):
	"""Command to remove files from AI context.

	Enables users to clean up context by removing files that are no
	longer relevant, reducing noise and improving AI focus on current task.
	Usage: `/drop old_file.py` -> removes file from AI awareness
	"""

	@property
	def name(self) -> str:
		return "drop"

	@property
	def description(self) -> str:
		return "Remove file from context"

	async def execute(self, args: str) -> None:
		"""Remove specified file from active context."""
		console = await self.make(Console)
		if not args:
			console.print("Usage: /drop <file_path>")
			return

		file_service: FileService = await self.make(FileService)
		if await file_service.remove_file(args):
			console.print(f"[success]Removed {args} from context[/success]")
			return
		else:
			console.print(f"[error]File {args} not found in context[/error]")
			return

	async def get_completions(self, text: str) -> List[str]:
		"""Provide completions showing files currently in the context.

		Returns relative paths of files in context that match the input pattern,
		allowing users to easily select which files to drop.
		Usage: Tab completion shows only files currently in AI context
		"""
		try:
			file_service = await self.make(FileService)

			# Get all files currently in context
			context_files = file_service.list_files()

			# Extract relative paths
			all_context_paths = [f.relative_path for f in context_files]

			# Filter by text pattern if provided
			if text:
				text_lower = text.lower()
				return [path for path in all_context_paths if text_lower in path.lower()]

			return all_context_paths
		except Exception:
			return []
