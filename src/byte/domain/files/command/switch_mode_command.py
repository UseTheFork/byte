from typing import List

from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.models import FileMode
from byte.domain.files.service.file_service import FileService


class SwitchModeCommand(Command):
	"""Command to switch file mode between editable and read-only.

	Allows users to change file permissions without removing and re-adding,
	useful when transitioning from exploration to editing phases.
	Usage: `/switch main.py` -> toggles between editable and read-only
	"""

	@property
	def name(self) -> str:
		return "switch"

	@property
	def category(self) -> str:
		return "Files"

	@property
	def description(self) -> str:
		return "Switch file mode between editable and read-only"

	async def execute(self, args: str) -> None:
		"""Switch the mode of a file in context."""
		console = await self.make(ConsoleService)

		if not args:
			console.print("Usage: /switch <file_path>")
			return

		file_service = await self.make(FileService)

		# Check if file is in context
		file_context = file_service.get_file_context(args)
		if not file_context:
			console.print(f"[error]File {args} not found in context[/error]")
			return

		# Determine new mode (toggle)
		new_mode = FileMode.READ_ONLY if file_context.mode == FileMode.EDITABLE else FileMode.EDITABLE

		# Switch the mode
		result = await file_service.set_file_mode(args, new_mode)

		if result:
			mode_str = "editable" if new_mode == FileMode.EDITABLE else "read-only"
			console.print(f"[success]Switched {args} to {mode_str} mode[/success]")
		else:
			console.print(f"[error]Failed to switch mode for {args}[/error]")

	async def get_completions(self, text: str) -> List[str]:
		"""Provide completions showing files currently in the context.

		Returns relative paths of files in context that match the input pattern,
		allowing users to easily select which files to switch.
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
