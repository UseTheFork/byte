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

    @dataclass
    class FileChanged(Event):
        # TODO: Doc String here.
        """"""

        file_path: str
        change_type: str

    @dataclass
    class FileStats(Event):
        """Event emitted when file statistics are updated."""

        editable: int = 0
        read_only: int = 0
