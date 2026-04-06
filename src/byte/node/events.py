from dataclasses import dataclass

from langchain_core.runnables import RunnableConfig

from byte.event import Event
from byte.orchestration import BaseState


class NodeEvents:
    """Namespace for all node based event types."""

    @dataclass
    class EndNode(Event):
        """"""

        state: BaseState
        agent: str

    @dataclass
    class PreAssistantNode(Event):
        """"""

        state: dict
        config: RunnableConfig
