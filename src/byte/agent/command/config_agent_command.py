from argparse import Namespace
from typing import List

from byte.agent import AgentConfigBoolSchema, AgentConfigStringSchema
from byte.cli import ByteArgumentParser, Command, InputCancelledError, InteractionService
from byte.support import Str


class ConfigAgentCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "config:agent"

    @property
    def category(self) -> str:
        return "Config"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Configure agent-specific settings",
        )
        parser.add_argument(
            "agent",
            type=str,
            help="Name of the agent to configure",
        )
        return parser

    def boot(self, *args, **kwargs) -> None:
        from byte.agent import AgentServiceProvider

        agent_service_provider = self.app.make(AgentServiceProvider)

        # Get all available agents and convert to string names
        self.agent_names = [Str.class_to_name(agent) for agent in agent_service_provider.agents()]

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Configure settings for the specified agent."""

        console = self.app["console"]
        interaction_service = self.app.make(InteractionService)

        agent_name = args.agent

        # Validate that the agent exists
        if agent_name not in self.agent_names:
            console.print_error(f"Agent '{agent_name}' not found. Available agents: {', '.join(self.agent_names)}")
            return

        # Get agent instance
        from byte.agent import AgentServiceProvider

        agent_service_provider = self.app.make(AgentServiceProvider)
        agent_class = next(cls for cls in agent_service_provider.agents() if Str.class_to_name(cls) == agent_name)
        agent = self.app.make(agent_class)

        # Configuration loop
        while True:
            config_data = agent.config().all()

            if not config_data:
                console.print_warning(f"Agent '{agent_name}' has no configurable settings.")
                return

            # Build menu options: "name: current_value" + "Done"
            options = [f"{config.name}: {config.value}" for key, config in config_data.items()]
            options.append("Done")

            try:
                choice = await interaction_service.select_numbered(f"Configure {agent_name}", options)
                if choice is None:
                    console.print_info("Configuration cancelled.")
                    return
            except InputCancelledError:
                console.print_info("Configuration cancelled.")
                return

            if choice == "Done":
                console.print_success("Configuration saved.")
                break

            # Extract name from "name: value" format
            selected_name = choice.split(":")[0].strip()

            # Find the key by matching name
            key = next(k for k, v in config_data.items() if v.name == selected_name)
            config_schema = config_data[key]

            if isinstance(config_schema, AgentConfigBoolSchema):
                try:
                    new_value = await self.prompt_for_confirmation(
                        f"{config_schema.description}", default=config_schema.value
                    )
                    if new_value is None:
                        continue
                except InputCancelledError:
                    continue
            elif isinstance(config_schema, AgentConfigStringSchema):
                try:
                    new_value = await self.prompt_for_input(
                        f"New value for {config_schema.name} (current: {config_schema.value}):"
                    )
                    if new_value is None or new_value == "":
                        continue
                except InputCancelledError:
                    continue

            # Update config
            config_schema.value = new_value
            agent.config().add(key, config_schema)
            console.print_success(f"Updated {config_schema.name} to {new_value}")

    async def get_completions(self, text: str) -> List[str]:
        """Provide agent name completions for the agent argument."""

        try:
            # Filter agents that match the current text input
            matches = [name for name in self.agent_names if name.lower().startswith(text.lower())]

            return matches
        except Exception:
            # Fallback to empty list if discovery fails
            return []
