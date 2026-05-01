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
    from byte.files.tools.add_files_tool import AddFilesTool
    from byte.files.tools.delete_file_tool import DeleteFileTool
    from byte.files.tools.edit_file_tool import EditFileTool
    from byte.files.tools.list_files_tool import ListFilesTool
    from byte.files.tools.replace_file_tool import ReplaceFileTool
    from byte.files.tools.write_file_tool import WriteFileTool

__all__ = (
    "AICommentWatcherService",
    "AddFileCommand",
    "AddFilesTool",
    "DeleteFileTool",
    "DropFileCommand",
    "EditFileTool",
    "FileContext",
    "FileDiscoveryService",
    "FileEvents",
    "FileIgnoreService",
    "FileMode",
    "FileService",
    "FileServiceProvider",
    "FileWatcherService",
    "ListFilesCommand",
    "ListFilesTool",
    "ReadOnlyCommand",
    "ReloadFilesCommand",
    "ReplaceFileTool",
    "SwitchModeCommand",
    "ToolFileService",
    "WriteFileTool",
)

_dynamic_imports = {
    # keep-sorted start
    "AICommentWatcherService": "service.ai_comment_watcher_service",
    "AddFileCommand": "command.add_file_command",
    "DeleteFileTool": "tools.delete_file_tool",
    "DropFileCommand": "command.drop_file_command",
    "EditFileTool": "tools.edit_file_tool",
    "FileContext": "models",
    "FileDiscoveryService": "service.discovery_service",
    "FileEvents": "events",
    "FileIgnoreService": "service.ignore_service",
    "FileMode": "models",
    "FileService": "service.file_service",
    "FileServiceProvider": "service_provider",
    "FileWatcherService": "service.watcher_service",
    "ListFilesCommand": "command.list_files_command",
    "ListFilesTool": "tools.list_files_tool",
    "AddFilesTool": "tools.add_files_tool",
    "ReadOnlyCommand": "command.add_read_only_file_command",
    "ReloadFilesCommand": "command.reload_files_command",
    "ReplaceFileTool": "tools.replace_file_tool",
    "SwitchModeCommand": "command.switch_mode_command",
    "ToolFileService": "service.tool_file_service",
    "WriteFileTool": "tools.write_file_tool",
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
