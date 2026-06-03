from dataclasses import dataclass

from byte.event import Event


class FileEvents:
    """Namespace for all file based event types."""

    @dataclass
    class FileAdded(Event):
        """Event emitted when a file is added to context."""

        file_path: str
        action: str = "context_added"

    @dataclass
    class FileChanged(Event):
        """Event emitted when a file in context is changed."""

        file_path: str
        change_type: str
