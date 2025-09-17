import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    """Base event class for domain events in the system.

    Provides automatic ID generation and timestamping for event tracking.
    Usage: `class FileAdded(Event): file_path: str`
    """

    event_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
