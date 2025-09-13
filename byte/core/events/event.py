import uuid
from abc import ABC
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event(ABC):
    """Base event class for domain events in the system.
    
    Provides automatic ID generation and timestamping for event tracking.
    Usage: `class FileAdded(Event): file_path: str`
    """

    event_id: str | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        # Generate unique ID for event tracing and debugging
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
        # Capture creation time for event ordering and audit trails
        if self.timestamp is None:
            self.timestamp = datetime.now()
