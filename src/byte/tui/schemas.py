import asyncio
import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from langchain_core.messages import BaseMessage

if TYPE_CHECKING:
    from byte import Command


@dataclass
class Answer:
    """An answer to a question posed by the agent."""

    label: str
    value: Any
    is_default: bool = False


@dataclass
class AnswerCancelled:
    pass


@dataclass
class Ask:
    question: str
    options: list[Answer] | None
    result_future: asyncio.Future[Answer | list[Answer] | str | AnswerCancelled]


@dataclass
class ChatMessage:
    message: BaseMessage
    timestamp: datetime.datetime | None


@dataclass
class AutocompleteOption:
    name: str
    description: str | None = None
    type: Literal["command"] | None = None
    command: Command | None = None  # Store the actual command instance for argument completion
