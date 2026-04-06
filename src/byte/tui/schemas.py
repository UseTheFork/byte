import asyncio
import datetime
from dataclasses import dataclass
from typing import Literal, NamedTuple

from langchain_core.messages import BaseMessage

from byte import Command

"""
allow_once - Allow this operation only this time
allow_always - Allow this operation and remember the choice
reject_once - Reject this operation only this time
reject_always - Reject this operation and remember the choice
"""


class Answer(NamedTuple):
    """An answer to a question posed by the agent."""

    text: str
    id: str


type Options = list[Answer]


@dataclass
class Ask:
    question: str
    options: Options
    result_future: asyncio.Future[Answer]


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
