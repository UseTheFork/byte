"""Files domain for file context management and project discovery."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.domain.files.command.add_file_command import AddFileCommand
    from byte.domain.files.command.add_read_only_file_command import ReadOnlyCommand
    from byte.domain.files.command.drop_file_command import DropFileCommand
    from byte.domain.files.command.list_files_command import ListFilesCommand
    from byte.domain.files.command.reload_files_command import ReloadFilesCommand
    from byte.domain.files.command.switch_mode_command import SwitchModeCommand
    from byte.domain.files.models import FileContext, FileMode
    from byte.domain.files.service.ai_comment_watcher_service import AICommentWatcherService
    from byte.domain.files.service.discovery_service import FileDiscoveryService
    from byte.domain.files.service.file_service import FileService
    from byte.domain.files.service.ignore_service import FileIgnoreService
    from byte.domain.files.service.watcher_service import FileWatcherService

__all__ = (
    "AICommentWatcherService",
    "AddFileCommand",
    "DropFileCommand",
    "FileContext",
    "FileDiscoveryService",
    "FileIgnoreService",
    "FileMode",
    "FileService",
    "FileWatcherService",
    "ListFilesCommand",
    "ReadOnlyCommand",
    "ReloadFilesCommand",
    "SwitchModeCommand",
)

_dynamic_imports = {
    # keep-sorted start
    "AICommentWatcherService": "service.ai_comment_watcher_service",
    "AddFileCommand": "command.add_file_command",
    "DropFileCommand": "command.drop_file_command",
    "FileContext": "models",
    "FileDiscoveryService": "service.discovery_service",
    "FileIgnoreService": "service.ignore_service",
    "FileMode": "models",
    "FileService": "service.file_service",
    "FileWatcherService": "service.watcher_service",
    "ListFilesCommand": "command.list_files_command",
    "ReadOnlyCommand": "command.add_read_only_file_command",
    "ReloadFilesCommand": "command.reload_files_command",
    "SwitchModeCommand": "command.switch_mode_command",
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
