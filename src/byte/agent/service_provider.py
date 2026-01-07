from typing import List, Type

from byte import Service, ServiceProvider
from byte.agent import (
    Agent,
    AgentService,
    AskAgent,
    AskCommand,
    AssistantNode,
    CleanerAgent,
    CoderAgent,
    CommitAgent,
    CommitPlanAgent,
    ConventionAgent,
    ConventionCommand,
    CopyAgent,
    CopyNode,
    EndNode,
    ExtractNode,
    LintNode,
    Node,
    ParseBlocksNode,
    ResearchAgent,
    ResearchCommand,
    ShowAgent,
    ShowCommand,
    ShowNode,
    StartNode,
    SubprocessAgent,
    SubprocessNode,
    ToolNode,
    ValidationNode,
)
from byte.cli import Command


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
            CommitPlanAgent,
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

    async def register(self) -> None:
        # Create all agents
        for agent_class in self.agents():
            self.app.singleton(agent_class)

        # Create all Nodes
        for node_class in self.nodes():
            self.app.bind(node_class)
