from typing import cast

from langchain_core.messages import AIMessage
from rich.columns import Columns
from rich.progress_bar import ProgressBar

from byte.core.event_bus import Payload
from byte.core.service.base_service import Service
from byte.domain.cli.rich.panel import Panel
from byte.domain.llm.service.llm_service import LLMService


class AgentAnalyticsService(Service):
    """Service for tracking and displaying AI agent analytics and token usage.

    Monitors token consumption across different models and provides visual feedback
    to users about their usage patterns and limits through rich progress displays.
    """

    async def boot(self):
        """Initialize analytics service and register event listeners.

        Sets up token tracking and registers the pre-prompt hook to display
        usage statistics before each user interaction.
        """
        self.reset_usage()

    async def update_usage_analytics_hook(self, payload: Payload) -> Payload:
        state = payload.get("state", {})
        llm = payload.get("llm", {})

        if messages := state.get("messages", []):
            message = messages[-1]

            # Check if message is an AIMessage before processing
            if not isinstance(message, AIMessage):
                return payload

            message = cast(AIMessage, message)

            # Extract usage metadata and total tokens
            usage_metadata = message.usage_metadata
            if usage_metadata:
                total_tokens = usage_metadata.get("total_tokens", 0)
                input_tokens = usage_metadata.get("input_tokens", 0)
                output_tokens = usage_metadata.get("output_tokens", 0)

                llm_service = await self.make(LLMService)

                if llm_service._service_config.main.model == llm.model:
                    # Update the main model context used with total tokens
                    self.model_usage["main"]["context"] = total_tokens
                    self.model_usage["main"]["total_input"] += input_tokens
                    self.model_usage["main"]["total_output"] += output_tokens

                if llm_service._service_config.weak.model == llm.model:
                    self.model_usage["weak"]["total_input"] += input_tokens
                    self.model_usage["weak"]["total_output"] += output_tokens

        return payload

    async def usage_panel_hook(self, payload: Payload) -> Payload:
        """Display token usage analytics panel with progress bars.

        Shows current token consumption for both main and weak models
        with visual progress indicators to help users track their usage.
        """
        llm_service = await self.make(LLMService)

        info_panel = payload.get("info_panel", [])

        # Calculate usage percentages
        main_percentage = min(
            (
                self.model_usage["main"]["context"]
                / llm_service._service_config.main.max_input_tokens
            )
            * 100,
            100,
        )

        weak_cost = (
            self.model_usage["weak"]["total_input"]
            * llm_service._service_config.weak.input_cost_per_token
        ) + (
            self.model_usage["weak"]["total_output"]
            * llm_service._service_config.weak.output_cost_per_token
        )

        main_cost = (
            self.model_usage["main"]["total_input"]
            * llm_service._service_config.main.input_cost_per_token
        ) + (
            self.model_usage["main"]["total_output"]
            * llm_service._service_config.main.output_cost_per_token
        )

        # llm_service._service_config.main.model

        progress = ProgressBar(
            total=llm_service._service_config.main.max_input_tokens,
            completed=self.model_usage["main"]["context"],
            width=20,
            complete_style="success",
        )

        analytics_panel = Panel(
            Columns(
                [
                    "Memory Used:",
                    progress,
                    f"{main_percentage:.1f}%",
                    "|",
                    "Main:",
                    f"{self.model_usage['main']['total_input']:,}",
                    f"(${main_cost:.2f})",
                    "|",
                    "Weak:",
                    f"{self.model_usage['weak']['total_input']:,}",
                    f"(${weak_cost:.2f})",
                ],
                expand=False,
            ),
            title="Analytics",
            border_style="primary",
        )

        info_panel.append(analytics_panel)
        return payload.set("info_panel", info_panel)

    def reset_usage(self):
        """Reset token usage counters to zero.

        Useful for starting fresh sessions or after reaching certain milestones.
        """
        self.model_usage = {
            "main": {
                "context": 0,
                "total_input": 0,
                "total_output": 0,
            },
            "weak": {
                "context": 0,
                "total_input": 0,
                "total_output": 0,
            },
        }
