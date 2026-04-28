from pathlib import Path

from byte import Service
from byte.files import FileDiscoveryService, FileMode, FileService
from byte.tui import InteractionService, Messages


class ToolFileService(Service):
    """ """

    def _prepare_file_path(self, path: str) -> Path:
        """Validate file path exists and is not read-only.

        Returns:
            Tuple of (is_valid, status_or_message). BlockStatus if invalid, empty string if valid.

        Usage: `valid, status = self._validate_file_path()` -> (BlockStatus, "") or (BlockStatus, MESSAGE)
        """

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

    async def edit_file(self, path: str, old_string: str, new_string: str) -> str:
        try:
            full_path = self._prepare_file_path(path)

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
        except Exception as e:
            self.emit_tui(
                Messages.CreatePanel(
                    str(e),
                    title="Tool Error",
                    border_style="warning",
                )
            )
            raise e

    async def write_file(self, path: str, content: str) -> str:
        """Write content to a file. Creates parent directories if needed.

        Confirms with the user before creating the file.

        Returns:
            Success or error message

        Usage: `result = await service.write_file(path, content)` -> "Successfully wrote X characters to 'path'"
        """
        try:
            full_path = self._prepare_file_path(path)
            interaction_service = self.app.make(InteractionService)

            if await interaction_service.confirm(
                f"Write to file '{path}'?",
                True,
            ):
                # Create parent directories if they don't exist
                full_path.parent.mkdir(parents=True, exist_ok=True)

                full_path.write_text(content, encoding="utf-8")
                return f"Successfully wrote {len(content)} characters to '{path}'"
            else:
                raise Exception("User declined request to write file.")

        except Exception as e:
            self.emit_tui(
                Messages.CreatePanel(
                    str(e),
                    title="Tool Error",
                    border_style="warning",
                )
            )
            raise e

    async def replace_file(self, path: str, content: str) -> str:
        """Replace all content of a file.

        Confirms with the user before replacing the file content.

        Returns:
            Success or error message

        Usage: `result = await service.replace_file(path, content)` -> "Successfully replaced content in 'path'"
        """
        try:
            full_path = self._prepare_file_path(path)
            interaction_service = self.app.make(InteractionService)

            if not full_path.exists():
                raise Exception(f"Error: File '{path}' does not exist")

            if await interaction_service.confirm(
                f"Replace all content in '{path}'?",
                True,
            ):
                full_path.write_text(content, encoding="utf-8")
                return f"Successfully replaced content in '{path}'"
            else:
                raise Exception("User declined request to replace file.")

        except Exception as e:
            self.emit_tui(
                Messages.CreatePanel(
                    str(e),
                    title="Tool Error",
                    border_style="warning",
                )
            )
            raise e

    async def delete_file(self, path: str):
        """Apply the delete operation to the file system.

        Deletes the file and removes it from both the file discovery service
        and file service context to ensure it's no longer tracked.

        Returns:
            Tuple of (status, error_message). BlockStatus.APPLIED if successful,
            appropriate error status otherwise with error message.

        Usage: `status, error = block.apply()` -> (BlockStatus.APPLIED, "") or (BlockStatus.INVALID, "error message")
        """
        try:
            file_discovery_service = self.app.make(FileDiscoveryService)
            file_service = self.app.make(FileService)

            interaction_service = self.app.make(InteractionService)
            resolved_file_path = self._prepare_file_path(path)

            if not resolved_file_path.exists():
                raise Exception(f"Error: File '{path}' does not exist")

            if await interaction_service.confirm(
                f"Delete '{path}'?",
                True,
            ):
                resolved_file_path.unlink()

                # Remove the deleted file from context
                await file_discovery_service.remove_file(resolved_file_path)
                await file_service.remove_file(str(resolved_file_path))
            else:
                raise Exception("User declined request to delete file.")

        except Exception as e:
            self.emit_tui(
                Messages.CreatePanel(
                    str(e),
                    title="Tool Error",
                    border_style="warning",
                )
            )
            raise e
