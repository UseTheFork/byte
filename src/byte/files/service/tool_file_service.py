from pathlib import Path
from typing import Dict

from byte import Service
from byte.files import FileContext, FileMode, FileService


class ToolFileService(Service):
    """ """

    def boot(self, **kwargs) -> None:
        """Initialize file service and ensure discovery service is ready."""
        self._context_files: Dict[str, FileContext] = {}

    async def edit_file(self, path: str, old_string: str, new_string: str) -> str:
        full_path = self.app.path(path)

        if not full_path.exists():
            raise Exception(f"Error: File '{path}' does not exist")

        content = full_path.read_text(encoding="utf-8")

        # Check how many times the old_string appears
        count = content.count(old_string)

        if count == 0:
            raise Exception(
                "Error: String not found in file. Make sure you're using the exact string including whitespace."
            )

        if count > 1:
            raise Exception(f"Error: String appears {count} times. Provide more context to make it unique.")

        # Perform the replacement
        new_content = content.replace(old_string, new_string, 1)
        full_path.write_text(new_content, encoding="utf-8")

        return f"Successfully edited '{path}'"

    def _prepare_file_path(self, path: str) -> Path:
        """Validate file path exists and is not read-only.

        Returns:
            Tuple of (is_valid, status_or_message). BlockStatus if invalid, empty string if valid.

        Usage: `valid, status = self._validate_file_path()` -> (BlockStatus, "") or (BlockStatus, MESSAGE)
        """

        self.app["log"].info(path)

        file_service = self.app.make(FileService)
        file_path = Path(path)

        # If the path is relative, resolve it against the project root
        if not file_path.is_absolute():
            resolved_file_path = self.app.root_path(str(file_path)).resolve()
        else:
            resolved_file_path = file_path.resolve()

        # Check if file is in read-only context
        file_context = file_service.get_file_context(resolved_file_path)

        if file_context and file_context.mode == FileMode.READ_ONLY:
            raise Exception(f"Cannot edit read-only file '{path}'.")

        # Check if file is outside project
        project_root = Path(self.app.root_path())

        try:
            resolved_file_path.resolve().relative_to(project_root.resolve())
        except ValueError:
            raise Exception(f"File is outside project root: {file_path}.")

        return resolved_file_path
