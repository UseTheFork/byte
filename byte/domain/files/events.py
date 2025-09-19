from byte.domain.events.event import Event
from byte.domain.files.context_manager import FileMode


class FileAdded(Event):
    """Event fired when a file is added to the AI context.

    Enables other parts of the system to react to context changes,
    such as updating UI displays or triggering persistence operations.
    Usage: `await self.event(FileAdded(file_path="main.py", mode=FileMode.EDITABLE))`
    """

    file_path: str = ""
    mode: FileMode = FileMode.READ_ONLY


class FileRemoved(Event):
    """Event fired when a file is removed from the AI context.

    Allows cleanup operations and UI updates when files are no longer
    part of the active context, maintaining system consistency.
    Usage: `await self.event(FileRemoved(file_path="old_file.py"))`
    """

    file_path: str = ""


class FileModeChanged(Event):
    """Event fired when a file's access mode changes.

    Notifies interested components when files transition between
    read-only and editable modes, enabling appropriate UI updates.
    Usage: `await self.event(FileModeChanged(file_path="config.py", old_mode=READ_ONLY, new_mode=EDITABLE))`
    """

    file_path: str = ""
    old_mode: FileMode = FileMode.READ_ONLY
    new_mode: FileMode = FileMode.READ_ONLY


class ContextCleared(Event):
    """Event fired when the entire file context is cleared.

    Signals a major context change that may require UI refresh
    or cleanup of related state throughout the system.
    Usage: `await self.event(ContextCleared())`
    """

    pass


class FileDeleted(Event):
    """Event fired when a file is deleted from the file system.

    Enables automatic cleanup of context and other file-related state
    when files are removed from the project directory.
    Usage: `await self.event(FileDeleted(file_path="/path/to/deleted/file.py"))`
    """

    file_path: str = ""


class AICommentDetected(Event):
    """Event fired when an AI comment pattern is detected in a file.

    Triggers automatic context management and potential completion workflows
    when files contain instruction comments like '// TODO:' or '# TODO:'.
    Usage: `await self.event(AICommentDetected(file_path="main.py", comment_content="fix this bug", line_number=42))`
    """

    file_path: str = ""
    comment_content: str = ""
    line_number: int = 0


class FileModified(Event):
    """Event fired when a file is created, modified, or deleted.

    General file system change event that other services can listen to
    for various file monitoring and synchronization needs.
    Usage: `await self.event(FileModified(file_path="main.py", change_type="modified"))`
    """

    file_path: str = ""
    change_type: str = ""  # "created", "modified", "deleted"
