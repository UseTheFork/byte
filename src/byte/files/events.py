from dataclasses import dataclass

from byte.event import Event


class FileEvents:
    """Namespace for all file based event types."""

    @dataclass
    class FileAdded(Event):
        """Event emitted when a file is added to context."""

        file_path: str
        mode: str
        action: str = "context_added"
        meta_editable_files: int = 0
        meta_read_only_files: int = 0

    @dataclass
    class FileChanged(Event):
        # TODO: Doc String here.
        """"""

        file_path: str
        change_type: str
