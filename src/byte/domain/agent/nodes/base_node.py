from abc import ABC

from langgraph.graph.state import RunnableConfig

from byte.core.mixins.bootable import Bootable
from byte.domain.agent.state import BaseState


class Node(ABC, Bootable):
    async def __call__(self, state: BaseState, config: RunnableConfig):
        pass
