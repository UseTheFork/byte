from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ResponseType(Enum):
    """Types of agent responses that need different handling."""

    TEXT_CHUNK = "text_chunk"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    THINKING = "thinking"
    STATE_UPDATE = "state_update"
    ERROR = "error"


@dataclass(frozen=True)
class ResponseChunk:
    """Normalized representation of an agent response chunk."""

    type: ResponseType
    content: str
    metadata: Optional[Dict[str, Any]] = None
    raw_chunk: Optional[Any] = None


@dataclass(frozen=True)
class ResponseOptions:
    """Configuration options for response handling."""

    show_thinking: bool = False
    show_tool_calls: bool = True
    show_tool_results: bool = True
    verbose: bool = False
    color_scheme: str = "default"
