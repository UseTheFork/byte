from typing import cast

from langchain_core.messages import AIMessage
from rich.console import Group
from rich.progress_bar import ProgressBar
from rich.table import Table

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

				if llm_service._service_config.main.params.model == llm.model:
					# Update the main model context used with total tokens
					self.model_usage["main"]["context"] = total_tokens
					self.model_usage["main"]["total"]["input"] += input_tokens
					self.model_usage["main"]["total"]["output"] += output_tokens
					self.model_usage["last"]["input"] = input_tokens
					self.model_usage["last"]["output"] = output_tokens
					self.model_usage["last"]["type"] = "main"

				if llm_service._service_config.weak.params.model == llm.model:
					self.model_usage["weak"]["total"]["input"] += input_tokens
					self.model_usage["weak"]["total"]["output"] += output_tokens
					self.model_usage["last"]["input"] = input_tokens
					self.model_usage["last"]["output"] = output_tokens
					self.model_usage["last"]["type"] = "weak"

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
			(self.model_usage["main"]["context"] / llm_service._service_config.main.constraints.max_input_tokens) * 100,
			100,
		)

		weak_cost = (
			self.model_usage["weak"]["total"]["input"]
			* llm_service._service_config.weak.constraints.input_cost_per_token
		) + (
			self.model_usage["weak"]["total"]["output"]
			* llm_service._service_config.weak.constraints.output_cost_per_token
		)

		main_cost = (
			self.model_usage["main"]["total"]["input"]
			* llm_service._service_config.main.constraints.input_cost_per_token
		) + (
			self.model_usage["main"]["total"]["output"]
			* llm_service._service_config.main.constraints.output_cost_per_token
		)

		# llm_service._service_config.main.model

		progress = ProgressBar(
			total=llm_service._service_config.main.constraints.max_input_tokens,
			completed=self.model_usage["main"]["context"],
			complete_style="success",
		)

		session_cost = main_cost + weak_cost

		# Calculate last message cost based on which model type was used
		last_message_type = self.model_usage["last"]["type"]
		if last_message_type == "main":
			last_message_cost = (
				self.model_usage["last"]["input"] * llm_service._service_config.main.constraints.input_cost_per_token
			) + (
				self.model_usage["last"]["output"] * llm_service._service_config.main.constraints.output_cost_per_token
			)
		elif last_message_type == "weak":
			last_message_cost = (
				self.model_usage["last"]["input"] * llm_service._service_config.weak.constraints.input_cost_per_token
			) + (
				self.model_usage["last"]["output"] * llm_service._service_config.weak.constraints.output_cost_per_token
			)
		else:
			last_message_cost = 0.0

		last_input = self.humanizer(self.model_usage["last"]["input"])
		last_output = self.humanizer(self.model_usage["last"]["output"])

		grid = Table.grid(expand=True)
		grid.add_column()
		grid.add_column(ratio=1)
		grid.add_column()
		grid.add_row("Memory Used ", progress, f" {main_percentage:.1f}%")

		grid_cost = Table.grid(expand=True)
		grid_cost.add_column()
		grid_cost.add_column(justify="right")
		grid_cost.add_row(
			f"Tokens: {last_input} sent, {last_output} received",
			f"Cost: ${last_message_cost:.2f} message, ${session_cost:.2f} session.",
		)

		analytics_panel = Panel(
			Group(grid, grid_cost),
			title="Analytics",
		)

		info_panel.append(analytics_panel)
		return payload.set("info_panel", info_panel)

	def reset_usage(self):
		"""Reset token usage counters to zero.

		Useful for starting fresh sessions or after reaching certain milestones.
		"""
		self.model_usage = {
			"last": {"input": 0, "output": 0, "type": ""},
			"main": {
				"context": 0,
				"total": {
					"input": 0,
					"output": 0,
				},
			},
			"weak": {
				"context": 0,
				"total": {
					"input": 0,
					"output": 0,
				},
			},
		}

	def reset_context(self) -> None:
		"""Reset context token counters for both main and weak models.

		Clears the current context usage while preserving total session usage.
		Useful when starting a new conversation or clearing the message history.
		"""
		self.model_usage["main"]["context"] = 0
		self.model_usage["weak"]["context"] = 0

	def humanizer(self, number: int | float) -> str:
		divisor = 1
		for suffix in ("K", "M", "B", "T"):
			divisor *= 1000
			max_allowed = divisor * 1000
			quotient, remainder = divmod(number, divisor)
			if number > max_allowed:
				continue
			if quotient:
				break
			return str(number)
		if remaining := (remainder and round(remainder / divisor, 1)):
			quotient += remaining
		return f"{quotient}{suffix}"
