import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    """Base event class with middleware-style payload support.

    Events can carry mutable payloads that listeners can modify,
    enabling middleware-style processing chains.
    Usage: `event = FileAdded(file_path="main.py", payload={"validated": False})`
    """

    event_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    payload: Dict[str, Any] = Field(default_factory=dict)

    # Control flags for middleware behavior
    stop_propagation: bool = False
    prevent_default: bool = False
