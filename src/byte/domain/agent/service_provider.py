from typing import List, Type

from byte.container import Container
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.agent.implementations.ask.agent import AskAgent
from byte.domain.agent.implementations.ask.command import AskCommand
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.cleaner.agent import CleanerAgent
from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.agent.implementations.commit.agent import CommitAgent
from byte.domain.agent.implementations.conventions.agent import ConventionAgent
from byte.domain.agent.implementations.conventions.command import ConventionCommand
from byte.domain.agent.implementations.copy.agent import CopyAgent
from byte.domain.agent.implementations.research.agent import ResearchAgent
from byte.domain.agent.implementations.research.command import ResearchCommand
from byte.domain.agent.implementations.show.agent import ShowAgent
from byte.domain.agent.implementations.show.command import ShowCommand
from byte.domain.agent.implementations.subprocess.agent import SubprocessAgent
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.nodes.copy_node import CopyNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.extract_node import ExtractNode
from byte.domain.agent.nodes.lint_node import LintNode
from byte.domain.agent.nodes.parse_blocks_node import ParseBlocksNode
from byte.domain.agent.nodes.show_node import ShowNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.nodes.subprocess_node import SubprocessNode
from byte.domain.agent.nodes.tool_node import ToolNode
from byte.domain.agent.nodes.validation_node import ValidationNode
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.service.command_registry import Command


class AgentServiceProvider(ServiceProvider):
    """Main service provider for all agent types and routing.

    Manages registration and initialization of specialized AI agents (coder, docs, ask)
    and provides the central agent switching functionality. Coordinates between
    different agent implementations while maintaining a unified interface.
    Usage: Automatically registered during bootstrap to enable agent routing
    """

    def services(self) -> List[Type[Service]]:
        return [AgentService]

    def agents(self) -> List[Type[Agent]]:
        return [
            # keep-sorted start
            AskAgent,
            CleanerAgent,
            CoderAgent,
            CommitAgent,
            ConventionAgent,
            CopyAgent,
            ResearchAgent,
            ShowAgent,
            SubprocessAgent,
            # keep-sorted end
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            # keep-sorted start
            AskCommand,
            ConventionCommand,
            ResearchCommand,
            ShowCommand,
            # keep-sorted end
        ]

    def nodes(self) -> List[Type[Node]]:
        return [
            # keep-sorted start
            AssistantNode,
            CopyNode,
            EndNode,
            ExtractNode,
            LintNode,
            ParseBlocksNode,
            ShowNode,
            StartNode,
            SubprocessNode,
            ToolNode,
            ValidationNode,
            # keep-sorted end
        ]

    async def register(self, container: Container) -> None:
        # Create all agents
        for agent_class in self.agents():
            container.singleton(agent_class)

        # Create all Nodes
        for node_class in self.nodes():
            container.bind(node_class)
