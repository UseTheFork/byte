from pathlib import Path

from byte import Service
from byte.files import FileDiscoveryService, FileService
from byte.tui import InteractionService, Messages


class ToolFileService(Service):
    """Manage file operations for tool interactions."""

    def boot(self, **kwargs) -> None:
        """Initialize the file service dependencies."""
        self.file_discovery_service = self.app.make(FileDiscoveryService)
        self.file_service = self.app.make(FileService)

    def _prepare_file_path(self, path: str) -> Path:
        """Validate file path is valid and within project."""

        file_path = Path(path)

        # If the path is relative, resolve it against the project root
        if not file_path.is_absolute():
            resolved_file_path = (self.app["path"] / str(file_path)).resolve()
        else:
            resolved_file_path = file_path.resolve()

        # Check if file is outside project
        project_root = self.app["path"]

        try:
            resolved_file_path.resolve().relative_to(project_root.resolve())
        except ValueError:
            raise Exception(f"File is outside project root: `{file_path}`.")

        return resolved_file_path

    async def edit_file(self, path: str, old_string: str, new_string: str) -> str:
        """Replace a substring in a file with exact matching."""
        try:
            full_path = self._prepare_file_path(path)

            if not full_path.exists():
                raise Exception(f"Error: File `{path}` does not exist")

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

            return f"Successfully edited `{path}`"
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
        """Write content to a file and create parent directories if needed."""
        try:
            full_path = self._prepare_file_path(path)
            interaction_service = self.app.make(InteractionService)

            if await interaction_service.confirm(
                f"Write to file `{path}`?",
                True,
            ):
                # Create parent directories if they don't exist
                full_path.parent.mkdir(parents=True, exist_ok=True)

                full_path.write_text(content, encoding="utf-8")

                await self.file_discovery_service.add_file(full_path)
                await self.file_service.add_file(str(full_path))

                return f"Successfully wrote {len(content)} characters to `{path}`"
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
        """Replace all content in a file."""
        try:
            full_path = self._prepare_file_path(path)

            if not full_path.exists():
                raise Exception(f"Error: File `{path}` does not exist")

            full_path.write_text(content, encoding="utf-8")
            return f"Successfully replaced content in `{path}`"

        except Exception as e:
            self.emit_tui(
                Messages.CreatePanel(
                    str(e),
                    title="Tool Error",
                    border_style="warning",
                )
            )
            raise e

    async def delete_file(self, path: str) -> str:
        """Delete a file and remove it from tracking services."""
        try:
            interaction_service = self.app.make(InteractionService)
            resolved_file_path = self._prepare_file_path(path)

            if not resolved_file_path.exists():
                raise Exception(f"Error: File `{path}` does not exist")

            if await interaction_service.confirm(
                f"Delete `{path}`?",
                True,
            ):
                resolved_file_path.unlink()

                # Remove the deleted file from context
                await self.file_discovery_service.remove_file(resolved_file_path)
                await self.file_service.remove_file(str(resolved_file_path))

                return f"Successfully deleted `{path}`"
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
