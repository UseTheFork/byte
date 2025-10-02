from typing import cast

from langchain_core.messages import AIMessage
from rich.columns import Columns
from rich.progress_bar import ProgressBar

from byte.core.event_bus import Payload
from byte.core.service.base_service import Service
from byte.domain.cli_output.rich.panel import Panel
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
        self.main_model_context_used = 0
        self.main_model_tokens_used = 0
        self.weak_model_tokens_used = 0

    async def update_usage_analytics(self, payload: Payload) -> Payload:
        processed_event = payload.get("processed_event", {})

        if messages := processed_event.get("messages", []):
            message = messages[-1]

            # Check if message is an AIMessage before processing
            if not isinstance(message, AIMessage):
                return payload

            message = cast(AIMessage, message)

            # Extract usage metadata and total tokens
            usage_metadata = message.usage_metadata
            if usage_metadata:
                total_tokens = usage_metadata.get("total_tokens", 0)

                llm_service = await self.make(LLMService)

                # Extract model name from response metadata
                model_name = message.response_metadata.get("model_name", "unknown")

                if llm_service._service_config.main.model == model_name:
                    # Update the main model context used with total tokens
                    self.main_model_context_used = total_tokens
                    self.main_model_tokens_used += total_tokens

                if llm_service._service_config.weak.model == model_name:
                    self.weak_model_tokens_used += total_tokens

        return payload

    async def display_usage_panel(self, payload: Payload) -> Payload:
        """Display token usage analytics panel with progress bars.

        Shows current token consumption for both main and weak models
        with visual progress indicators to help users track their usage.
        """
        llm_service = await self.make(LLMService)

        info_panel = payload.get("info_panel", [])

        # Calculate usage percentages
        main_percentage = min(
            (self.main_model_context_used / llm_service._service_config.main.max_tokens)
            * 100,
            100,
        )

        weak_cost = (
            self.weak_model_tokens_used
            * llm_service._service_config.weak.cost_per_token
        )

        main_cost = (
            self.main_model_tokens_used
            * llm_service._service_config.main.cost_per_token
        )

        # llm_service._service_config.main.model

        progress = ProgressBar(
            total=llm_service._service_config.main.max_tokens,
            completed=self.main_model_context_used,
            width=15,
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
                    f"{self.main_model_tokens_used:,}",
                    f"(${main_cost:.2f})",
                    "|",
                    "Weak:",
                    f"{self.weak_model_tokens_used:,}",
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
        self.main_model_context_used = 0
        self.main_model_tokens_used = 0
        self.weak_model_tokens_used = 0
