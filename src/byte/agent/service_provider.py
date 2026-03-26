from typing import List, Type

from byte import Service, ServiceProvider
from byte.agent import (
    AskAgent,
    AssistantNode,
    BaseAgent,
    CoderAgent,
    ConfigAgentCommand,
    EndNode,
    ExtractNode,
    LintNode,
    MainModelNode,
    Node,
    ParseBlocksNode,
    ReasoningModelNode,
    RoutingNode,
    StartNode,
    ToolNode,
    ValidationNode,
    WeakModelNode,
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
        return []

    def agents(self) -> List[Type[BaseAgent]]:
        return [
            # keep-sorted start
            AskAgent,
            # CleanerAgent,
            CoderAgent,
            # CommitAgent,
            # CommitPlanAgent,
            # ConventionAgent,
            # ResearchAgent,
            # keep-sorted end
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            # keep-sorted start
            ConfigAgentCommand,
            # ResearchCommand,
            # keep-sorted end
        ]

    def nodes(self) -> List[Type[Node]]:
        return [
            # keep-sorted start
            AssistantNode,
            EndNode,
            ExtractNode,
            LintNode,
            MainModelNode,
            ParseBlocksNode,
            ReasoningModelNode,
            RoutingNode,
            StartNode,
            ToolNode,
            ValidationNode,
            WeakModelNode,
            # keep-sorted end
        ]

    def register(self) -> None:
        # Create all agents
        for agent_class in self.agents():
            self.app.singleton(agent_class)

        # Create all Nodes
        for node_class in self.nodes():
            self.app.bind(node_class)
