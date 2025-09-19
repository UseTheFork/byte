# byte/domain/agent/commands.py
from typing import List

from rich.console import Console

from byte.core.command.registry import Command
from byte.domain.agent.service import AgentService
from byte.domain.agent.state import CommandProcessor


class SwitchAgentCommand(Command):
    """Command to switch between different AI agents (coder, docs, ask, etc.).

    Enables users to change the active agent that processes regular input,
    allowing specialized AI behavior for different tasks like coding,
    documentation, or general questions.
    Usage: `/agent coder` -> switches to coding agent for technical tasks
    """

    @property
    def name(self) -> str:
        return "agent"

    @property
    def description(self) -> str:
        return "Switch between AI agents (coder, docs, ask)"

    async def execute(self, args: str) -> None:
        """Switch to the specified agent.

        Usage: `await command.execute("coder")` -> activates coder agent
        """
        args = args.strip()

        if not args:
            # Show current agent and available options
            await self._show_agent_status()
            return

        agent_service = await self.make(AgentService)
        command_processor = await self.make(CommandProcessor)
        console = await self.make(Console)

        if agent_service.set_active_agent(args):
            # Update command processor's active agent
            command_processor.set_active_agent(args)
            console.print(f"[green]✓[/green] Switched to {args} agent")
        else:
            available_agents = self._get_available_agents()
            console.print(f"[error]Unknown agent: {args}[/error]")
            console.print(f"Available agents: {', '.join(available_agents)}")

    def get_completions(self, text: str) -> List[str]:
        pass
        """Provide tab completion for available agent names.

        Usage: `/agent c<TAB>` -> suggests "coder"
        """
        available_agents = self._get_available_agents()

        if not text:
            return available_agents

        return [agent for agent in available_agents if agent.startswith(text.lower())]

    def _get_available_agents(self) -> List[str]:
        """Get list of available agent names for completion and validation."""
        # This could be dynamic based on registered agents
        return ["coder", "docs", "ask"]  # Expand as you add more agents

    async def _show_agent_status(self) -> None:
        """Show current agent and available options."""
        agent_service = await self.make(AgentService)
        console = await self.make(Console)

        current_agent = agent_service.get_active_agent()
        available_agents = self._get_available_agents()

        console.print(f"[bold]Current agent:[/bold] {current_agent}")
        console.print(f"[bold]Available agents:[/bold] {', '.join(available_agents)}")
        console.print("\n[dim]Usage: /agent <name> to switch[/dim]")
