import uuid
from abc import ABC
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event(ABC):
    """Base event class."""

    event_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()
