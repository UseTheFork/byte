import datetime

from langchain_core.messages import BaseMessage
from pydantic.dataclasses import dataclass


@dataclass
class ChatMessage:
    message: BaseMessage
    timestamp: datetime.datetime | None
