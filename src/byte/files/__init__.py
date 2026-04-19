"""Files domain for file context management and project discovery."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.files.command.add_file_command import AddFileCommand
    from byte.files.command.add_read_only_file_command import ReadOnlyCommand
    from byte.files.command.drop_file_command import DropFileCommand
    from byte.files.command.list_files_command import ListFilesCommand
    from byte.files.command.reload_files_command import ReloadFilesCommand
    from byte.files.command.switch_mode_command import SwitchModeCommand
    from byte.files.events import FileEvents
    from byte.files.models import FileContext, FileMode
    from byte.files.service.ai_comment_watcher_service import AICommentWatcherService
    from byte.files.service.discovery_service import FileDiscoveryService
    from byte.files.service.file_service import FileService
    from byte.files.service.ignore_service import FileIgnoreService
    from byte.files.service.tool_file_service import ToolFileService
    from byte.files.service.watcher_service import FileWatcherService
    from byte.files.service_provider import FileServiceProvider
    from byte.files.tools.delete_file import delete_file
    from byte.files.tools.edit_file import edit_file
    from byte.files.tools.replace_file import replace_file
    from byte.files.tools.write_file import write_file

__all__ = (
    "AICommentWatcherService",
    "AddFileCommand",
    "DropFileCommand",
    "FileContext",
    "FileDiscoveryService",
    "FileEvents",
    "FileIgnoreService",
    "FileMode",
    "FileService",
    "FileServiceProvider",
    "FileWatcherService",
    "ListFilesCommand",
    "ReadOnlyCommand",
    "ReloadFilesCommand",
    "SwitchModeCommand",
    "ToolFileService",
    "delete_file",
    "edit_file",
    "replace_file",
    "write_file",
)

_dynamic_imports = {
    # keep-sorted start
    "AICommentWatcherService": "service.ai_comment_watcher_service",
    "AddFileCommand": "command.add_file_command",
    "DropFileCommand": "command.drop_file_command",
    "FileContext": "models",
    "FileDiscoveryService": "service.discovery_service",
    "FileEvents": "events",
    "FileIgnoreService": "service.ignore_service",
    "FileMode": "models",
    "FileService": "service.file_service",
    "FileServiceProvider": "service_provider",
    "FileWatcherService": "service.watcher_service",
    "ListFilesCommand": "command.list_files_command",
    "ReadOnlyCommand": "command.add_read_only_file_command",
    "ReloadFilesCommand": "command.reload_files_command",
    "SwitchModeCommand": "command.switch_mode_command",
    "ToolFileService": "service.tool_file_service",
    "delete_file": "tools.delete_file",
    "edit_file": "tools.edit_file",
    "replace_file": "tools.replace_file",
    "write_file": "tools.write_file",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
