from langgraph.graph.state import CompiledStateGraph, RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState


class SubgraphNode(Node):
    """ """

    async def boot(
        self,
        built_agent: CompiledStateGraph,
        **kwargs,
    ):
        """ """
        self.built_agent = built_agent

    async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
        """Execute subprocess command and optionally add results to messages.

        Args:
                state: SubprocessState containing the command to execute
                config: LangGraph runnable configuration

        Returns:
                Command with optional message update if user confirms adding results

        Usage: Called automatically by SubprocessAgent during graph execution
        """

        return self.built_agent
        return Command(goto="end_node")
